import json
import subprocess
from csv import DictWriter
from datetime import datetime
from os import mkdir, path, remove
from typing import Any, Dict, List, Tuple, cast

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import (
    AbstractBaseUser,
    AnonymousUser,
    Group,
    User,
)
from django.core.files import File
from django.db import connection
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import redirect, render
from django.utils.encoding import smart_str
from django.views.generic import TemplateView

from .forms import EmailForm, LoginForm
from .models import QueryWizardQuery

# from django_stubs_ext.db.models import TypedModelMeta


class IndexView(TemplateView):
    template_name = "web/index.jinja"


def collate_metadata(
    request: HttpRequest,
    query_results: List[Dict[Any, Any]],
    directory_name: str,
    file_to_download: str,
) -> None:
    """
    Collate data returned from SQL query, render into csv, save csv to tmp
    directory. For scalar write all data. For 3D write only metadata.
    """
    output_file_name = path.join(
        settings.DOWNLOAD_ROOT,
        directory_name,
        file_to_download,
    )
    with open(
        output_file_name,
        "w",
        newline="",  # request.session['newline_char'] added a newline on each row
    ) as f:
        csv_file = File(f)
        meta_names = [
            m[0] for m in get_specimen_metadata(request.session["scalar_or_3d"])
        ]
        if request.session["scalar_or_3d"].lower() == "3d":
            meta_names.append("missing points (indexed by specimen starting at 1)")
            variable_names = []
        else:
            # variable_names = [ v[0] for v in request.session.keys() ]
            variable_names = request.session["variable_labels"]
        writer = DictWriter(
            csv_file, fieldnames=meta_names + variable_names, extrasaction="ignore"
        )

        # This so I can replace default header, i.e. fieldnames, with custom header.
        # Note to self: since I'm using DictWriter I don't have to worry about
        # the ordering of the header being different from the order of the subsequent
        # rows: it takes care of that.
        headers = {
            m[0]: m[1] for m in get_specimen_metadata(request.session["scalar_or_3d"])
        }
        headers.update({v: v for v in variable_names})
        writer.writerow(headers)

        if request.session["scalar_or_3d"].lower() == "3d":
            meta_names.append("missing points (indexed by specimen starting at 1)")
            rows = request.session["3d_metadata"]
        else:
            rows = tabulate_scalar(query_results, False)
        for row in rows:
            in_dict = {k: row[k] for k in row.keys()}
            if request.session["scalar_or_3d"].lower() == "3d":
                in_dict.update(
                    {"missing_pts": request.session["missing_pts"][row["specimen_id"]]}
                )
            writer.writerow(in_dict)


def stream_scalar_export(request: HttpRequest, output_file_name: str) -> None:
    """
    Run the (unbounded) scalar query and write the CSV directly as rows are
    fetched, instead of first collecting the full result set into a list
    (as collate_metadata/tabulate_scalar do). Rows are grouped into one CSV
    row per specimen as they arrive, relying on the query's
    `ORDER BY specimen_id` so a specimen's rows are never split across
    groups.
    """
    with connection.cursor() as variable_query:
        variable_query.execute(
            "SELECT label "
            "  FROM variable "
            " WHERE variable.id "
            "    IN %s "
            "ORDER BY label ASC;",
            [request.session["table_selections"]["variable"]],
        )
        request.session["variable_labels"] = [
            label[0] for label in variable_query.fetchall()
        ]

    sql_query = set_up_sql_query(True)
    params = [
        get_accessible_group_ids(request.user),
        request.session["table_selections"]["sex"],
        request.session["table_selections"]["fossil"],
        request.session["table_selections"]["taxon"],
        request.session["table_selections"]["variable"],
    ]

    meta_names = [m[0] for m in get_specimen_metadata("Scalar")]
    variable_names = request.session["variable_labels"]
    headers = {m[0]: m[1] for m in get_specimen_metadata("Scalar")}
    headers.update({v: v for v in variable_names})

    with open(output_file_name, "w", newline="") as f:
        writer = DictWriter(
            File(f), fieldnames=meta_names + variable_names, extrasaction="ignore"
        )
        writer.writerow(headers)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            columns = [col[0] for col in cursor.description]
            current_specimen = None
            current_dict: Dict[str, str] | None = None
            for db_row in cursor:
                row = dict(zip(columns, db_row))
                if row["specimen_id"] != current_specimen:
                    if current_dict is not None:
                        writer.writerow(current_dict)
                    current_dict = init_query_table("Scalar", row)
                    current_specimen = row["specimen_id"]
                assert current_dict is not None
                current_dict[row["variable_label"]] = row["scalar_value"]
            if current_dict is not None:
                writer.writerow(current_dict)


# def concat_variable_list(myList):
#     """
#     Return myList as comma-separated string of values enclosed in parens.
#     """
#     return "(" + reduce((lambda b, c: b + str(c) + ","), myList, "")[:-1] + ")"


def build_tree_json(
    model_name: str, selected_ids: list[int]
) -> tuple[list[dict], dict[str, bool]]:
    """
    Build a nested tree structure and initial selection map for the React tree
    component. Returns (tree_data, selection) where tree_data is a list of root
    nodes and selection maps str(id) -> bool.
    """
    model = apps.get_model(app_label="web", model_name=model_name.capitalize())
    all_nodes = list(
        model.objects.values("id", "label", "parent_id", "expand_in_tree", "tree_root")
    )
    selected_set = set(selected_ids)

    node_map: dict[int, dict] = {
        n["id"]: {
            "id": n["id"],
            "label": n["label"],
            "expand_in_tree": bool(n["expand_in_tree"]),
            "children": [],
        }
        for n in all_nodes
    }

    roots: list[dict] = []
    for n in all_nodes:
        nid = n["id"]
        pid = n["parent_id"]
        if n.get("tree_root") or pid == nid:
            roots.append(node_map[nid])
        elif pid in node_map:
            node_map[pid]["children"].append(node_map[nid])

    selection = {str(n["id"]): n["id"] in selected_set for n in all_nodes}
    return roots, selection


def download(
    scalar_or_3d: str, directory_name: str, file_to_download: str
) -> HttpResponse:
    """
    Download one of csv, Morphologika, GRFND. File has been written to path
    before this is called.
    """
    # request.session[
    #     "page_title"
    # ] = f"PRIMO Download {scalar_or_3d} Data"
    if scalar_or_3d.lower() == "3d":
        filepath = path.join(settings.DOWNLOAD_ROOT, directory_name)
    else:
        filepath = path.join(settings.DOWNLOAD_ROOT, file_to_download)

    if path.exists(filepath):
        if scalar_or_3d.lower() == "3d":
            # Just as a reminer, -c is create a new file; -z is gzip it;
            # -f is filename; -C is move to the following directory first;
            # name at end is the directory to compress.
            # Using -C here to get rid of prefix of absolute file path.
            # So: tar -czf DOWNLOAD_ROOT/filename.tar.gz -C DOWNLOAD_ROOT directory_name
            # Files should be in directory_name, so that directory is
            # what needs to be compressed, meaning tar needs to operate from
            # DOWNLOAD_ROOT.
            subprocess.run(
                [
                    "tar",
                    "-czf",
                    path.join(
                        settings.DOWNLOAD_ROOT,
                        directory_name + ".tar.gz",
                    ),
                    "-C",
                    settings.DOWNLOAD_ROOT,
                    directory_name,
                ],
                check=False,
            )
            # We have to reset filepath here because now we've tarred it.
            filepath = path.join(settings.DOWNLOAD_ROOT, directory_name + ".tar.gz")
        with open(filepath, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response["Content-Disposition"] = "inline; filename=%s" % smart_str(
                path.basename(file_to_download)
            )
            response["X-Sendfile"] = smart_str(filepath)
            return response
    raise Http404


def download_success(request: HttpRequest) -> HttpResponse:
    """TODO: Is this in use?"""
    request.session["page_title"] = "Download Success"
    return render(request, "web/download_success.jinja", {})


BACKUP_TABLES = {"specimen", "session", "data_scalar"}
UPLOAD_TABLES = {"session", "data_scalar"}


def _get_backups() -> dict[str, list[tuple[str, str]]]:
    """Return {base_table: [(backup_name, label), ...]} sorted newest-first."""
    import re

    pattern = re.compile(r"^(.+)_(\d{8})_(\d{4})$")
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        all_tables = [row[0] for row in cursor.fetchall()]
    backups: dict[str, list[tuple[str, str]]] = {t: [] for t in BACKUP_TABLES}
    for name in all_tables:
        m = pattern.match(name)
        if m and m.group(1) in BACKUP_TABLES:
            try:
                dt = datetime.strptime(f"{m.group(2)}_{m.group(3)}", "%Y%m%d_%H%M")
                label = dt.strftime("%-d %B %Y, %H:%M").replace(
                    dt.strftime("%-d"), _ordinal(dt.day), 1
                )
            except ValueError:
                label = name
            backups[m.group(1)].append((name, label))
    for pairs in backups.values():
        pairs.sort(key=lambda x: x[0], reverse=True)
    return backups


def _ordinal(n: int) -> str:
    suffix = (
        "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )
    return f"{n}{suffix}"


@staff_member_required
def delete_backup(request: HttpRequest) -> HttpResponse:
    message = None
    message_class = "success"
    confirm_backup = None
    confirm_table = None
    confirm_label = None

    if request.method == "POST":
        backup_name = request.POST.get("backup", "")
        import re

        m = re.match(r"^(.+)_\d{8}_\d{4}$", backup_name)
        if not m or m.group(1) not in BACKUP_TABLES:
            message = f"Invalid backup: {backup_name}"
            message_class = "errornote"
        elif request.POST.get("confirmed") == "1":
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE `{backup_name}`")
                message = f"Deleted backup: {backup_name}"
            except Exception as e:
                message = f"Delete failed: {e}"
                message_class = "errornote"
        else:
            confirm_backup = backup_name
            confirm_table = m.group(1)
            try:
                dt = datetime.strptime(
                    backup_name[len(confirm_table) + 1 :], "%Y%m%d_%H%M"
                )
                confirm_label = dt.strftime("%-d %B %Y, %H:%M").replace(
                    dt.strftime("%-d"), _ordinal(dt.day), 1
                )
            except ValueError:
                confirm_label = backup_name

    return render(
        request,
        "admin/restore.html",
        {
            "message": message,
            "message_class": message_class,
            "title": "Restore / Delete Backups",
            "backups": _get_backups(),
            "confirm_backup": confirm_backup,
            "confirm_table": confirm_table if confirm_backup else None,
            "confirm_label": confirm_label,
            "confirm_action": "delete",
        },
    )


@staff_member_required
def restore_table(request: HttpRequest) -> HttpResponse:
    message = None
    message_class = "success"
    confirm_backup = None
    confirm_table = None
    confirm_label = None

    if request.method == "POST":
        backup_name = request.POST.get("backup", "")
        import re

        m = re.match(r"^(.+)_\d{8}_\d{4}$", backup_name)
        if not m or m.group(1) not in BACKUP_TABLES:
            message = f"Invalid backup: {backup_name}"
            message_class = "errornote"
        elif request.POST.get("confirmed") == "1":
            table = m.group(1)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE `{table}`")
                    cursor.execute(f"RENAME TABLE `{backup_name}` TO `{table}`")
                message = f"Restored {backup_name} to {table}"
            except Exception as e:
                message = f"Restore failed: {e}"
                message_class = "errornote"
        else:
            confirm_backup = backup_name
            confirm_table = m.group(1)
            try:
                dt = datetime.strptime(
                    backup_name[len(confirm_table) + 1 :], "%Y%m%d_%H%M"
                )
                confirm_label = dt.strftime("%-d %B %Y, %H:%M").replace(
                    dt.strftime("%-d"), _ordinal(dt.day), 1
                )
            except ValueError:
                confirm_label = backup_name

    return render(
        request,
        "admin/restore.html",
        {
            "message": message,
            "message_class": message_class,
            "title": "Restore Table",
            "backups": _get_backups(),
            "confirm_backup": confirm_backup,
            "confirm_table": confirm_table,
            "confirm_label": confirm_label,
            "confirm_action": "restore",
        },
    )


@staff_member_required
def upload_csv(request: HttpRequest) -> HttpResponse:
    message = None
    message_class = "success"
    if request.method == "POST":
        table = request.POST.get("table", "")
        csv_file = request.FILES.get("csv_file")
        if table not in UPLOAD_TABLES:
            message = f"Invalid table: {table}"
            message_class = "errornote"
        elif not csv_file:
            message = "No file selected."
            message_class = "errornote"
        elif not csv_file.name or not csv_file.name.endswith(".csv"):
            message = "File must be a CSV."
            message_class = "errornote"
        else:
            filename: str = csv_file.name
            tmp_path = path.join(settings.DOWNLOAD_ROOT, filename)
            try:
                with open(tmp_path, "wb") as f:
                    for chunk in csv_file.chunks():
                        f.write(chunk)
                remove(tmp_path)
                message = f"File '{filename}' received successfully."
            except Exception as e:
                message = f"Upload failed: {e}"
                message_class = "errornote"
    return render(
        request,
        "admin/upload.html",
        {"message": message, "message_class": message_class, "title": "Update Tables"},
    )


@staff_member_required
def backup_table(request: HttpRequest) -> HttpResponse:
    message = None
    message_class = "success"
    if request.method == "POST":
        table = request.POST.get("table", "")
        if table not in BACKUP_TABLES:
            message = f"Invalid table: {table}"
            message_class = "errornote"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            backup_name = f"{table}_{timestamp}"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE TABLE `{backup_name}` AS SELECT * FROM `{table}`"
                    )
                message = f"Backup created: {backup_name}"
            except Exception as e:
                message = f"Backup failed: {e}"
                message_class = "errornote"
    return render(
        request,
        "admin/backup.html",
        {"message": message, "message_class": message_class, "title": "Back Up Table"},
    )


def email(request: HttpRequest) -> HttpResponse:
    """Render access request form; submission opens user's email client via mailto."""
    request.session["page_title"] = "Email Administrator"
    form = EmailForm()
    return render(request, "web/email.jinja", {"form": form})


def entity_relation_diagram(request: HttpRequest) -> HttpResponse:
    """Retrieve relational database table pdf."""
    request.session["page_title"] = "Database Structure"
    return render(request, "web/entity_relation_diagram.jinja", {})


def export(
    request: HttpRequest, scalar_or_3d: str, which_3d_output_type: str = ""
) -> HttpResponse:
    if not user_has_group_access(request.user):
        return HttpResponseForbidden(
            "Full downloads are only available to logged-in members. "
            "Preview-only accounts are limited to the five-specimen preview."
        )

    directory_name, file_to_download = set_up_download(request)
    if scalar_or_3d.lower() == "scalar":
        output_file_name = path.join(
            settings.DOWNLOAD_ROOT, directory_name, file_to_download
        )
        stream_scalar_export(request, output_file_name)
    else:
        _, query_results = execute_query(request, scalar_or_3d)
        collate_metadata(request, query_results, directory_name, file_to_download)
    request.session["page_title"] = f"PRIMO Download {scalar_or_3d} Data"
    return download(scalar_or_3d, directory_name, file_to_download)


def create_3d_output_string(
    request: HttpRequest, query_results: List[Dict[Any, Any]], output_file_type: str
) -> None:
    """
    Collate data returned from 3D SQL query.
    Print out two files: a csv of metadata and a GRFND file. Fields
    included in metadata are enumerated below.

    NOTE: unlike the scalar export path (see stream_scalar_export), this
    builds the entire output_str in memory before writing it out, and its
    caller (query_3d, currently disabled/commented out above) fetches the
    full 3D result set via a single unbounded cursor.fetchall(). 3D isn't
    exposed via any URL right now, so this hasn't caused problems, but if
    3D querying/export is reintroduced, it will need the same large-result
    treatment as the scalar path (SQL-level limiting for previews, streaming
    the query/write for downloads) or it can reintroduce the original
    "large query overloads the request" problem this issue was about.
    """

    newline_char = request.session["newline_char"]
    # missing_pts will be output in metadata csv file. key is specimen id,
    # value is string of missing points for specimen.

    missing_pts = {}

    # Header is different, otherwise files are nearly identical.
    num_query_results = len(query_results)
    num_sessions = len(request.session["sessions"])
    if output_file_type == "morpho":
        # Morphologika file format:
        # [individuals]
        # number of individuals
        # [landmarks]
        # number of landmarks (total specimens/total number of sampled points)
        #    where each sampled point has x, y, and z components
        # [dimensions]
        # 3
        # [names]
        # specimen ids
        # [rawpoints]
        # datapoints as x \t y \t z (TODO: are these ordered?)
        output_str = (newline_char * 2).join(
            [
                "[individuals]",
                str(num_query_results),
                "[landmarks]",
                str(num_query_results / num_sessions),
                "[dimensions]",
                "3",
                "[names]",
            ]
        )
    else:  # GRFND file
        # GRFND file format:
        # 1 number of individuals L 3*number of landmarks 1 9999 DIM-3
        # datapoints as x \t y \t z (TODO: are these ordered?)
        output_str = (
            f"1 {num_query_results}L "
            f"{3 * num_query_results / num_sessions} 1 9999 "
            f"DIM=3{newline_char}"
        )

    for row in query_results:
        output_str += f"{row['specimen_id']}{newline_char}"
    # data points
    if output_file_type == "morpho":
        output_str += f"{newline_char}[rawpoints]{newline_char}"
    # point_ctr will be used to track which points are missing for a given
    # sessiom/specimen.
    missing_point_ctr = 1
    current_specimen = -1  # Keeps track of when new specimen data starts.
    for row in query_results:
        if row["specimen_id"] != current_specimen:
            current_specimen = row["specimen_id"]
            if output_file_type == "morpho":
                output_str += (
                    newline_char
                    + "'"
                    + row["hypocode"].replace("/ /", "_")
                    + newline_char
                )
            else:
                output_str += newline_char
            missing_pts[row["specimen_id"]] = ""
            missing_point_ctr = 1
        if (
            str(row["x"]) == "9999.0"
            and str(row["y"]) == "9999.0"
            and str(row["z"]) == "9999.0"
        ):
            output_str += "9999\t9999\t9999" + newline_char
            missing_pts[row["specimen_id"]] += " " + str(missing_point_ctr)

        else:
            output_str += f"{row['x']}\t{row['y']}\t{row['z']}{newline_char}"

        missing_point_ctr += 1
    request.session["missing_pts"] = missing_pts

    with open(
        path.join(
            settings.DOWNLOAD_ROOT, request.session["directory_name"], "3d_data.txt"
        ),
        "w",
    ) as outfile:
        outfile.write(output_str)


def get_3D_data(request: HttpRequest) -> List[Dict[Any, Any]]:
    """Execute query for actual 3D points, i.e. not metadata."""

    base = (
        "SELECT DISTINCT session.id AS session_id, "
        "                specimen.id AS specimen_id, "
        "                specimen.hypocode AS hypocode, "
        "                data_3d.x, "
        "                data_3d.y, "
        "                data_3d.z, "
        "                data_3d.datindex, "
        "                data_3d.variable_id, "
        "                observer.researcher_name AS researcher_name "
        "FROM data_3d "
        "     JOIN variable ON data_3d.variable_id = variable.id"
        "     JOIN session ON data_3d.session_id = session.id"
        "     JOIN specimen ON session.specimen_id = specimen.id"
        "     JOIN observer ON session.observer_id = observer.id"
    )

    where = " WHERE session_id IN %s"
    # group_by = " GROUP BY session_id"
    ordering = " ORDER BY specimen_id, variable_id, data_3d.datindex ASC"
    final_sql = f"{base} {where} {ordering};"

    with connection.cursor() as cursor:
        cursor.execute(final_sql, [request.session["sessions"]])
        # Now return all rows as a dictionary object. Note that each variable
        # name will have its own row, so I'm going to have to jump through some
        # hoops to get the names out correctly for the table headers in the view.

        columns = [col[0] for col in cursor.description]
        query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    # Not a session variable because it's a dictionary.
    return query_results


def get_specimen_metadata(scalar_or_3d: str) -> list[Tuple[str, str]]:
    """
    Return a list of tuples with SQL column name:csv column name as key:value.
    Created a fn because this was called all over the place.
    """

    if scalar_or_3d.lower() == "3d":
        three_d_list = [
            ("protocol", "Protocol"),
            ("missing_pts", "Missing points (indexed by specimen starting at 1)"),
            ("session_id", "Session ID"),
        ]
    else:
        three_d_list = []
    return [
        ("specimen_id", "Specimen ID"),
        ("hypocode", "Hypocode"),
        ("collection_acronym", "Collection Acronym"),
        ("catalog_number", "Catalog No."),
        ("taxon_label", "Taxon name"),
        ("sex_type", "Sex"),
        ("taxonomic_type", "Type Status"),
        ("mass", "Mass"),
        ("fossil_or_extant", "Fossil or Extant"),
        ("captive_or_wild", "Captive or Wild"),
        ("original_or_cast", "Original or Cast"),
        ("session_comments", "Session Comments"),
        ("specimen_comments", "Specimen Comments"),
        #  ("age_class", "Age Class"),
        ("locality_name", "Locality"),
        ("country_name", "Country"),
        ("researcher_name", "Observer"),
    ] + three_d_list


def init_query_table(scalar_or_3d: str, query_result: Dict[str, str]) -> Dict[str, str]:
    """
    Initialize query table (actually a dictionary) that is to be used for data
    that will be pushed out to view. A single query row is received and put into
    dictionary.
    """
    output = {
        key[0]: query_result[key[0]] for key in get_specimen_metadata(scalar_or_3d)
    }
    output["variable_label"] = query_result["variable_label"]
    output["scalar_value"] = query_result["scalar_value"]
    return output


def log_in(request: HttpRequest) -> HttpResponse:
    request.session["page_title"] = "Login"
    form = LoginForm(request.POST or None)

    if "next" in request.GET:
        next_page = request.GET["next"]
    else:
        next_page = "/"
    if request.method == "POST" and form.is_valid():
        username = request.POST.get("user_name")
        password = request.POST.get("password")
        next_page = request.POST.get("next") or next_page
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            profile = getattr(user, "profile", None)
            if profile and profile.must_change_password:
                return redirect("change_password")
            return redirect(next_page)
        return render(
            request,
            "web/login.jinja",
            {
                "form": form,
                "error": (
                    "Your username/password combination"
                    " didn’t match. Please try again."
                ),
                "next": next_page,
            },
        )
    return render(
        request,
        "web/login.jinja",
        {
            "form": form,
            "next": next_page,
            "error": None,
        },
    )


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    error = None
    if request.method == "POST":
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if not new_password:
            error = "Password cannot be empty."
        elif new_password != confirm_password:
            error = "Passwords do not match."
        else:
            request.user.set_password(new_password)
            request.user.save()
            profile = getattr(request.user, "profile", None)
            if profile:
                profile.must_change_password = False
                profile.save()
            login(request, request.user)  # type: ignore[arg-type]
            return redirect("/")
    return render(request, "web/change_password.jinja", {"error": error})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    request.session["page_title"] = "Logout"
    logout(request)
    return render(request, "web/logout.jinja")


@login_required
def parameter_selection(request: HttpRequest, current_table: str = "") -> HttpResponse:
    """Select all parameters for current_table."""
    tree_data: list[dict] = []
    tree_selection: dict[str, bool] = {}
    request.session["page_title"] = f"{current_table.capitalize()} Selection"
    if current_table == "variable":
        if request.session["table_selections"]["bodypart"]:
            with connection.cursor() as variable_query:
                sql = (
                    "SELECT v.variable_name AS var_name, "
                    "       v.label AS var_label, "
                    "       v.id AS var_id, "
                    "       bps.id AS bodypart_id, "
                    "       bps.label AS bodypart_name "
                    "FROM variable v"
                    "    JOIN bodypart_variable bv"
                    "         ON v.id = bv.variable_id "
                    "    JOIN (SELECT bodypart.id, bodypart.label "
                    "            FROM bodypart "
                    "           WHERE id IN %s) AS bps "
                    "      ON bps.id = bv.bodypart_id "
                    "ORDER BY v.id"
                )

                variable_query.execute(
                    sql, [request.session["table_selections"]["bodypart"]]
                )
                columns = [col[0] for col in variable_query.description]
                vals = [dict(zip(columns, row)) for row in variable_query.fetchall()]
                if not vals:
                    messages.warning(
                        request,
                        (
                            "No variables are associated with the selected bodyparts. "
                            "Please reselect bodyparts."
                        ),
                    )

        else:
            vals = (
                apps.get_model(
                    app_label="web",
                    model_name=current_table.capitalize(),
                )
                .objects.values(
                    "variable_name",
                    "label",
                    "bodypartvariable__bodypart_id",
                )
                .all()
            )

    elif current_table in ("bodypart", "taxon"):
        vals = []
        tree_data, tree_selection = build_tree_json(
            current_table,
            request.session["table_selections"][current_table],
        )

    elif current_table in ("fossil", "sex"):
        current_model = apps.get_model(
            app_label="web",
            model_name=current_table.capitalize(),
        )
        vals = current_model.objects.values("id", "label").all()
    else:
        raise ValueError(f"Unexpected current_table value: {current_table!r}")

    selected_ids = set(request.session["table_selections"].get(current_table, []))

    return render(
        request,
        "web/parameter_selection.jinja",
        {
            "current_table": current_table,
            "values": vals,
            "selected_ids": selected_ids,
            "tree_data_json": json.dumps(tree_data),
            "tree_selection_json": json.dumps(tree_selection),
        },
    )


@login_required
def initialize_query(
    request: HttpRequest, scalar_or_3d: str = "Scalar"
) -> HttpResponse:
    """
    For scalar queries send parameter_selection to front end. Once all
    parameters are set, give option to call results, e.g. query_scalar().

    Tables will be all of the tables that are available to search on for a
    particular search type (e.g. scalar or 3D). Of those tables, sex and
    fossil will be pre-filled with all values selected. In that case,
    do a second query for all possible values and fill those values in.
    """
    request.session["page_title"] = f"{scalar_or_3d} Query Wizard"
    if request.method == "POST":
        # If there's a POST, then parameter_selection has been called and some
        # values have been sent back. But there's a possibility that we've changed
        # query types in the meantime, so check for that as well.
        current_table = request.POST.get("table")

        if request.POST.get("commit") == "Submit checked options":
            selected_rows: list[int] = [
                int(item) for item in request.POST.getlist("id")
            ]
            if request.POST.get("table") == "bodypart":
                request.session["table_selections"]["variable"] = []
            request.session["table_selections"][current_table] = selected_rows
    if not request.session["tables"] or request.session["scalar_or_3d"] != scalar_or_3d:
        # If tables isn't set, query for all tables and set up both tables and
        # selected lists. Note that "tables" will exist as key either way.
        # Note for this query that "tables" is set as the related name in Models.py.
        request.session["scalar_or_3d"] = scalar_or_3d
        tables = QueryWizardQuery.objects.get(
            data_table=scalar_or_3d.capitalize()
        ).tables.all()
        # selected will hold all preselected data (e.g. sex: [1, 2, 3, 4, 5, 9]).
        selected = {}
        request.session["tables"] = []
        request.session["table_selections"] = {}

        for table in tables:
            # if len(request.session['selected'][table.table_name]) == 0:
            request.session["tables"].append(
                {
                    "table_name": table.filter_table_name,
                    "display_name": table.display_name,
                }
            )

            if table.preselected:
                filter_table_name = table.filter_table_name
                if filter_table_name is None:
                    raise ValueError(f"Table {table} is missing filter_table_name")
                model = apps.get_model(
                    app_label="web",
                    model_name=filter_table_name.capitalize(),
                )
                values = model.objects.values("id").all()
                # Because vals is a list of dicts in format 'id': value.
                request.session["table_selections"][filter_table_name] = [
                    value["id"] for value in values
                ]
            else:
                request.session["table_selections"][table.filter_table_name] = []
                # So I can use 'if selected[table]' in initialize_query.jinja.

    selected = request.session["table_selections"]
    # I coudn't figure out any way to do this other than to check each time.
    finished = True

    for table in request.session["tables"]:
        if not selected[table["table_name"]]:
            finished = False

    request.session.modified = True
    return render(
        request,
        "web/initialize_query.jinja",
        {
            "scalar_or_3d": scalar_or_3d,
            "tables": request.session["tables"],
            "selected": selected,
            "finished": finished,
        },
    )


def _get_public_group_id() -> int | None:
    """Return the id of the 'non-member' group, or None if it doesn't exist."""
    try:
        return Group.objects.get(name="non-member").id
    except Group.DoesNotExist:
        return None


def get_accessible_group_ids(user: AbstractBaseUser | AnonymousUser) -> List[int]:
    """
    Return the list of session.group_id values `user` may query.

    Admin users (superuser, staff, or members of the 'admin' group) see all
    session groups. Every other visitor can see the 'non-member' group; authenticated
    users additionally see data in any other Django auth Group they belong to.
    If the 'non-member' group is missing, unauthenticated users get no results
    and authenticated users see only their own groups.
    """
    if user.is_authenticated:
        concrete = cast(User, user)
        if (
            concrete.is_superuser
            or concrete.is_staff
            or concrete.groups.filter(name="admin").exists()
        ):
            return list(Group.objects.values_list("id", flat=True))
    public_id = _get_public_group_id()
    group_ids: set[int] = {public_id} if public_id is not None else set()
    if user.is_authenticated:
        concrete = cast(User, user)
        group_ids.update(concrete.groups.values_list("id", flat=True))
    return list(group_ids)


def user_has_group_access(user: AbstractBaseUser | AnonymousUser) -> bool:
    """
    Return True if `user` should get full (non-preview) query results.

    This is true for authenticated users who belong to at least one group
    besides the 'non-member' public group. Unauthenticated visitors and users
    with no group membership beyond that only ever get a truncated preview.
    """
    if not user.is_authenticated:
        return False
    public_id = _get_public_group_id()
    qs = cast(User, user).groups
    return qs.exclude(id=public_id).exists() if public_id is not None else qs.exists()


def execute_query(
    request: HttpRequest, scalar_or_3d: str, limit_to_five: bool = False
) -> Tuple[str, List[Dict[Any, Any]]]:
    """Set up the query SQL. Do query. Call result table display."""
    if scalar_or_3d.lower() == "scalar":
        with connection.cursor() as variable_query:
            variable_query.execute(
                "SELECT label "
                "  FROM variable "
                " WHERE variable.id "
                "    IN %s "
                "ORDER BY label ASC;",
                [request.session["table_selections"]["variable"]],
            )
            request.session["variable_labels"] = [
                label[0] for label in variable_query.fetchall()
            ]

    group_ids = get_accessible_group_ids(request.user)

    sql_query = set_up_sql_query(True, limit_to_five)

    params = [
        group_ids,
        request.session["table_selections"]["sex"],
        request.session["table_selections"]["fossil"],
        request.session["table_selections"]["taxon"],
        request.session["table_selections"]["variable"],
    ]
    if limit_to_five:
        # The limiting subquery embeds a second copy of the WHERE clause
        # (see set_up_sql_query), so its params need to appear again too.
        params = params * 2

    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return sql_query, [dict(zip(columns, row)) for row in cursor.fetchall()]


def preview(request: HttpRequest) -> HttpResponse:
    """Set up the scalar query SQL. Do query. Call result table display."""
    request.session["page_title"] = f"{request.session['scalar_or_3d']} Results Preview"

    sql_query, query_results = execute_query(
        request, request.session["scalar_or_3d"], limit_to_five=True
    )

    are_results = True
    tabulated_query_results = tabulate_scalar(
        query_results,
        True,
    )

    are_results = bool(tabulated_query_results)

    group_ids = get_accessible_group_ids(request.user)
    count_params = [
        group_ids,
        request.session["table_selections"]["sex"],
        request.session["table_selections"]["fossil"],
        request.session["table_selections"]["taxon"],
        request.session["table_selections"]["variable"],
    ]
    count_sql = set_up_sql_query(True, count_only=True)
    with connection.cursor() as cursor:
        cursor.execute(count_sql, count_params)
        total_specimens: int = cursor.fetchone()[0]

    # This is for use in export_csv_file().
    submission_values = [
        group_ids,
        request.session["table_selections"]["sex"],
        request.session["table_selections"]["fossil"],
        request.session["table_selections"]["taxon"],
    ]
    if request.session["scalar_or_3d"].lower() == "scalar":
        submission_values.append(request.session["table_selections"]["variable"])
    # sql_query embeds the WHERE clause (and its %s placeholders) twice when
    # limit_to_five is used (see set_up_sql_query), so double these too.
    submission_values = submission_values * 2
    context = {
        "final_sql": sql_query.replace("%s", "{}").format(*submission_values),
        "are_results": are_results,
        "total_specimens": total_specimens,
        "preview_only": not user_has_group_access(request.user),
        "specimen_metadata": get_specimen_metadata(request.session["scalar_or_3d"]),
        "user": request.user.username,
        "query_results": tabulated_query_results,
    }
    if request.session["scalar_or_3d"].lower() == "scalar":
        context["variable_labels"] = request.session["variable_labels"]
        context["variable_ids"] = request.session["table_selections"]["variable"]
        context["query_results"] = tabulated_query_results
    else:
        # This is a list of all the session that will be returned from the query
        # so I can send it to `get_3D_data()` for a second query to get the actual data.
        # I'm using a set because each point is its own line in the output. A list
        # would have repeated data.
        sessions = set()
        for item in query_results:
            sessions.add(item["session_id"])
    return render(request, "web/preview.jinja", context)


@login_required
def query_start(request: HttpRequest) -> HttpResponse:
    """Start or reset query by creating or emptying data structures."""
    request.session["page_title"] = "Query Wizard"
    request.session["tables"] = []
    request.session["selected"] = {}
    request.session["selected"]["table"] = []
    request.session["scalar_or_3d"] = ""
    request.session["variable_labels"] = []
    # request.session['query_results'] = []
    return render(request, "web/query_start.jinja")


def set_up_sql_query(
    is_scalar: bool, limit_to_five: bool = False, count_only: bool = False
) -> str:
    """
    Create an SQL query for either 3D or scalar data. If limit_to_five,
    restrict to the first five specimens (by id) matching the filters,
    at the database level, instead of fetching every matching row.
    """

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    # TODO: maybe move this back into the DB?
    # Note we skip variables in 3D SELECT: we're getting all of them.
    select_common = ", ".join(
        [
            "specimen.id AS specimen_id",
            "specimen.hypocode AS hypocode",
            "session.id AS session_id",
            "institute.abbr AS collection_acronym",
            "specimen.catalog_number AS catalog_number",
            "taxon.label AS taxon_label",
            "specimen.mass AS mass",
            "sex.label AS sex_type",
            'COALESCE(taxonomic_type.taxonomic_type, "") AS taxonomic_type',
            "fossil.label AS fossil_or_extant",
            "captive.captive_or_wild",
            "original.original_or_cast",
            # "age_class.age_class",
            "locality.locality_name",
            "country.country_name",
            "specimen.comments AS specimen_comments",
            "session.comments AS session_comments",
            "observer.researcher_name AS researcher_name",
        ]
    )
    # session.group_id restricts results to groups the requesting user may
    # access (see get_accessible_group_ids); applies to both scalar and 3D.
    where = (
        "WHERE session.group_id IN %s "
        "AND sex.id IN %s AND fossil.id IN %s AND taxon.id IN %s"
    )

    if is_scalar:
        select_start = (
            "SELECT variable.label AS variable_label, "
            "       data_scalar.value AS scalar_value, "
        )
        from_start = " ".join(
            [
                "FROM variable"
                "     JOIN data_scalar"
                "       ON data_scalar.variable_id = variable.id"
                "     JOIN session"
                "       ON data_scalar.session_id = session.id"
            ]
        )
        where += " and variable.id in %s"
    else:
        # Is 3D.
        from_start = " ".join(
            [
                "FROM session",
                "     JOIN data_3d",
                "       ON session.id = data_3d.session_id",
            ]
        )
        select_start = "SELECT DISTINCT specimen.id AS specimen_id,"

    joins = " ".join(
        [
            "JOIN original",
            "  ON session.original_id = original.id",
            "JOIN specimen",
            "  ON session.specimen_id = specimen.id",
            "JOIN taxon",
            "  ON taxon.id = specimen.taxon_id",
            "JOIN sex",
            "  ON sex.id = specimen.sex_id",
            "JOIN fossil",
            "  ON fossil.id = specimen.fossil_id",
            "JOIN institute",
            "  ON institute.id = specimen.institute_id",
            "JOIN captive",
            "  ON captive.id = specimen.captive_id",
            "LEFT JOIN taxonomic_type",  # Some are NULL.
            "  ON taxonomic_type.id = specimen.taxonomic_type_id",
            # "JOIN age_class",
            # "  ON age_class.id = specimen.age_class_id",
            "LEFT JOIN locality",
            "  ON locality.id = specimen.locality_id",
            "LEFT JOIN country",
            "  ON country.id = locality.country_id",
            "JOIN observer",
            "  ON observer.id = session.observer_id",
        ]
    )

    ordering = "ORDER BY `specimen_id` ASC"

    if count_only:
        return f"SELECT COUNT(DISTINCT specimen.id) {from_start} {joins} {where};"

    if limit_to_five:
        # Scalar rows are one-per-variable, so a plain SQL LIMIT on the main
        # query could cut a specimen off mid-variable-list. Instead, limit
        # the specimen ids up front to the first five matching specimens,
        # and restrict the main query to just those ids.
        limiting_subquery = (
            f"SELECT DISTINCT specimen.id {from_start} {joins} {where} "
            "ORDER BY specimen.id ASC LIMIT 5"
        )
        where = (
            f"{where} AND specimen.id IN (SELECT id FROM "
            f"({limiting_subquery}) AS _preview)"
        )

    return f"{select_start} {select_common} {from_start} {joins} {where} {ordering};"


# def query_3d(request: HttpRequest, output_file_type: str) -> HttpResponse:
#     """
#     Set up the 3D query SQL. Do query for metadata. Call get_3D_data to get 3D
#     points. Send results to either Morphologika or GRFND creator and downloader.
#     If preview_only, ignore which_output_type and show metadata preview for top
#     five taxa.
#     Is this used?
#     """

#     preview_only = not user_has_group_access(request.user)

#     request.session["scalar_or_3d"] = "3D"
#     # request.session["output_file_type"] = output_file_type
#     # TODO: Look into doing this all with built-ins, rather than with .raw()
#     # TODO: Move all of this and 3D into db. As it was before, dammit.

#     # This is for cleaner code when composing header row for metadata csv.
#     # First value is field name in DB, second is header name for metadata csv.

#     # This is okay to include in publicly-available code (i.e. git), because
#     # the database structure diagram is already published on the website anyway.
#     # We'll only do metadata search first.

#     sql_query = set_up_sql_query(False, preview_only)

#     # This is a list of all the session that will be returned from the query
#     # so I can send it to `get_3D_data()` for a second query to get the actual data.
#     # I'm using a set because each point is its own line in the output. A list
#     # would have repeated data.
#     sessions = set()

#     with connection.cursor() as cursor:
#         cursor.execute(
#             sql_query,
#             [
#                 get_accessible_group_ids(request.user),
#                 request.session["table_var_select_done"]["sex"],
#                 request.session["table_var_select_done"]["fossil"],
#                 request.session["table_var_select_done"]["taxon"],
#             ],
#         )
#         # Now return all rows as a dictionary object. Note that each variable
#         # name will have its own row, so I'm going to have to jump through some
#         # hoops to get the names out correctly for the table headers in the view.

#         # TODO: There has to be a better way to do that.

#         # Note nice list comprehensions from the Django docs here:
#         columns = [col[0] for col in cursor.description]
#         query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         # Need to get session ids in case file will be downloaded.
#         # Single specimen per session is enforced at DB level.
#         # This won't be used for preview.
#         for item in query_results:
#             sessions.add(item["session_id"])

#     request.session["query"] = sql_query
#     request.session["sessions"] = list(sessions)
#     request.session["3d_metadata"] = query_results

#     context = {
#         "final_sql": sql_query.replace("%s", "{}")
#         .format(
#             request.session["table_var_select_done"]["sex"],
#             request.session["table_var_select_done"]["fossil"],
#             request.session["table_var_select_done"]["taxon"],
#         )
#         .replace("[", "(")
#         .replace("]", ")"),
#         "preview_only": preview_only,
#         "query_results": query_results,
#         "scalar_or_3d": request.session["scalar_or_3d"],
#         "specimen_metadata": get_specimen_metadata(request),
#         "total_specimens": len(
#             query_results
#         ),  # This should be the same as len(request.session['sessions'])
#         "user": request.user.username,
#     }

#     # If it's not a preview I need to get actual data and then send to Morphologika
#     # or GRFND.
#     if not preview_only:
#         query_results = get_3D_data(request)
#         export_3d(request, query_results, output_file_type)
#         # return render(request, 'web/download_success.jinja')

#     return render(request, "web/preview.jinja", context)


def set_up_download(request: HttpRequest) -> Tuple[str, str]:
    """
    Set the newline character, set name of file based on current time.
    Put both in session variable. If it's 3D make 3D output directory.
    """

    # Stupid Windows: we need to make sure the newline is set correctly.
    # Abundance of caution.
    newline_char = "\n"
    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    if "win" in user_agent:
        newline_char = "\r\n"
    request.session["newline_char"] = newline_char

    # This for use in download()
    # Reminder: The format of the file name will be yy-mm-dd_hh.mm.ss
    if request.session["scalar_or_3d"] == "3D":
        prefix = "PRIMO_metadata_"
    else:
        prefix = "PRIMO_results_"
    file_to_download = prefix + datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".csv"
    directory_name = ""
    if request.session["scalar_or_3d"] == "3D":
        directory_name = "PRIMO_3D_" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        file_to_download = "specimen_metadata.csv"
        mkdir(path.join(settings.DOWNLOAD_ROOT, directory_name))

    return directory_name, file_to_download


def tabulate_scalar(
    query_results: list[dict[str, str]], preview_only: bool
) -> list[Dict[str, str]]:
    """
    Return a list of dictionaries where each dictionary has the keys
    Specimen ID
    Hypocode
    Collection Acronym
    Catalog No.
    Taxon name
    Sex
    Fossil or Extant
    Captive or Wild
    Session Comments
    Specimen Comments
    Locality Name
    Country Name

    query_results must be ordered by specimen_id.
    """
    if not query_results:
        return []
    current_specimen = query_results[0]["specimen_id"]
    output = []
    current_dict = init_query_table("Scalar", query_results[0])
    num_specimens = 1
    for row in query_results:
        # Is this a new specimen? If so need to set up new empty dictionary and
        # append it.
        if row["specimen_id"] == current_specimen:
            current_dict[row["variable_label"]] = row["scalar_value"]
        else:
            num_specimens += 1
            output.append(current_dict)
            current_dict = init_query_table("Scalar", row)
            # This next so we can look up values quickly in view rather than
            # having to do constant conditionals.
            current_dict[row["variable_label"]] = row["scalar_value"]
            current_specimen = row["specimen_id"]
        if preview_only and num_specimens >= 5:
            break
    output.append(current_dict)
    return output
