import subprocess
from csv import DictWriter
from datetime import datetime
from os import mkdir, path
from sys import exc_info
from typing import Any, Dict, List, Tuple

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.mail import send_mail
from django.db import connection
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.encoding import smart_str
from django.views.generic import TemplateView

from .forms import EmailForm, LoginForm
from .models import QueryWizardQuery

# from django_stubs_ext.db.models import TypedModelMeta


class IndexView(TemplateView):
    template_name = "primo/index.jinja"


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
        # print("\n\n***VARIABLE NAMES", variable_names)
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
            rows = query_results
        for row in rows:
            inDict = {
                k: row[k]
                for k in row.keys()
                if k != "scalar_value" and k != "variable_label"
            }
            if request.session["scalar_or_3d"].lower() == "3d":
                inDict.update(
                    {"missing_pts": request.session["missing_pts"][row["specimen_id"]]}
                )
            writer.writerow(inDict)


# def concat_variable_list(myList):
#     """
#     Return myList as comma-separated string of values enclosed in parens.
#     """
#     return "(" + reduce((lambda b, c: b + str(c) + ","), myList, "")[:-1] + ")"


def create_tree_javascript(
    request: HttpRequest, parent_id: int, current_table: str
) -> str:
    """
    Create javascript for heirarchical tree display. Formal parameters for
    tree.add() are:
    add(node_id, parent_id, node name, url, icon, expand?, precheck?, extra info,
    text on mouse hover).
    Function is recursive on parent_id and returns a properly-formatted string
    of Javascript code.
    """

    # From reading nlstree docs (https://www.addobject.com/nlstree),
    # it seems order is unimportant, so recursion may be unnecessary (wasteful?).
    # Oh, wait: necessary because of if statement dealing with Eucatarrhini.
    # Okay, so *eventually* unnecessary?

    # The last two are currently unneeded, and therefore ignored below.
    javascript = ""
    js_item_delimiter = '", "'
    vals = (
        apps.get_model(
            app_label="primo",
            model_name=current_table.capitalize(),
        )
        .objects.values(
            "id",
            "label",
            "parent_id",
            "expand_in_tree",
        )
        .filter(parent_id=parent_id)
    )
    for val in vals:
        # Remove quote marks from `name`, as they'll screw up Javascript
        name = val["label"].replace('"', "")
        item_id = val["id"]
        parent_id = val["parent_id"]
        expand = "true" if val["expand_in_tree"] else "false"
        if name != "Eocatarrhini":
            # I'm not clear why I don't need to recurse up Eucatarrhini heirarchy.
            # Note that there's an extra blank entry for icon after the second item_id.
            javascript += (
                'tree.add("'
                + str(item_id)
                + js_item_delimiter
                + str(parent_id)
                + js_item_delimiter
                + name
                + js_item_delimiter
                + str(item_id)
                + js_item_delimiter
                + '", '
                + expand
                + ", "
            )
            if item_id not in request.session["table_var_select_done"][current_table]:
                javascript += "false );\n"
            else:
                javascript += "true );\n"
            javascript += create_tree_javascript(request, item_id, current_table)

    return javascript


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
                ]
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
    """Is this in use?"""
    request.session["page_title"] = "Download Success"
    return render(request, "primo/download_success.jinja", {})


def email(request: HttpRequest) -> HttpResponse:
    """Create email form, collect info, send email."""
    request.session["page_title"] = "Email Administrator"
    form = EmailForm(request.POST or None)
    error = None
    if request.method == "POST":
        if form.is_valid():
            # Get crap from POST. I'm using `type: ignore` here because I know
            # the form has already been validated and all of these fields exist.
            name = f"{request.POST.get('first_name')} {request.POST.get('last_name')}"
            email = f"{request.POST.get('email')},"
            body = (
                f"{name}, {email}\n"
                f"{request.POST.get('affiliation')},"
                f"{request.POST.get('position')},"
                f"{request.POST.get('dept')},"
                f"{request.POST.get('institute')}/n"
                f"{request.POST.get('country')}/n"
                f"{request.POST.get('body')}"
            )
            send_mail(
                "PRIMO access request",
                body,
                "primo@nycep.org",
                ["eric.delson@example.com"],
                fail_silently=False,
            )
            return render(
                request, "primo/email.jinja", {"success": True, "error": error}
            )
        # Form is not valid, so errors should print.
        return render(request, "primo/email.jinja", {"form": form})
    # There is no POST data, page hasn't loaded previously,
    return render(request, "primo/email.jinja", {"form": form})


def entity_relation_diagram(request: HttpRequest) -> HttpResponse:
    """Retrieve relational database table pdf."""
    request.session["page_title"] = "Database Structure"
    return render(request, "primo/entity_relation_diagram.jinja", {})


def export(
    request: HttpRequest, scalar_or_3d: str, which_3d_output_type: str = ""
) -> HttpResponse:
    _, query_results = execute_query(request, scalar_or_3d)

    directory_name, file_to_download = set_up_download(request)
    # print("\n\n***query results", query_results)
    collate_metadata(request, query_results, directory_name, file_to_download)
    request.session["page_title"] = f"PRIMO Download {scalar_or_3d} Data"
    return download(scalar_or_3d, directory_name, file_to_download)


# def export_scalar(request: HttpRequest) -> HttpResponse:
#     request.session["scalar_or_3d"] = "Scalar"
#     directory_name, file_to_download = set_up_download(request)
#     _, query_results = execute_query(request, "Scalar")
#     collate_metadata(request, query_results, directory_name, file_to_download)
#     return download(request, scalar_or_3d, directory_name, file_to_download)


# def export_3d(
#     request: HttpRequest, query_results: List[Dict[Any, Any]], output_file_type: str
# ) -> HttpResponse:
#     """Is this used?"""
#     #     request.session["output_file_type"] = output_file_type
#     request.session["scalar_or_3d"] = "3D"
#     directory_name, file_to_download = set_up_download(request)
#     _, query_results = execute_query(request, "3D")
#     create_3d_output_string(request, query_results, output_file_type)
#     collate_metadata(request, query_results, directory_name, file_to_download)
#     return download(request, scalar_or_3d, directory_name, file_to_download)


def create_3d_output_string(
    request: HttpRequest, query_results: List[Dict[Any, Any]], output_file_type: str
) -> None:
    """
    Collate data returned from 3D SQL query.
    Print out two files: a csv of metadata and a GRFND file. Fields
    included in metadata are enumerated below.
    """

    newline_char = request.session["newline_char"]
    """
    missing_pts will be output in metadata csv file. key is specimen id,
    value is string of missing points for specimen.
    """
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
    """
    point_ctr will be used to track which points are missing for a given
    sessiom/specimen.
    """
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
        # TODO: There has to be a better way to do that.

        # Note nice list comprehensions from the Django docs here:
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
        ("age_class", "Age Class"),
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
        next_page = request.POST.get("next")  # type: ignore
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect(next_page)
        else:
            return render(
                request,
                "primo/login.jinja",
                {
                    "form": form,
                    "error": """Your username/password combination
                                didn’t match. Please try again.""",
                    "next": next_page,
                },
            )
    else:
        return render(
            request,
            "primo/login.jinja",
            {
                "form": form,
                "next": next_page,
                "error": None,
            },
        )


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    request.session["page_title"] = "Logout"
    logout(request)
    return render(request, "primo/logout.jinja")


@login_required
def parameter_selection(request: HttpRequest, current_table: str = "") -> HttpResponse:
    """Select all parameters for current_table."""
    javascript = ""
    request.session["page_title"] = f"{current_table.capitalize()} Selection"
    if current_table == "variable":
        if request.session["table_var_select_done"]["bodypart"]:
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
                    sql, [request.session["table_var_select_done"]["bodypart"]]
                )
                columns = [col[0] for col in variable_query.description]
                vals = [dict(zip(columns, row)) for row in variable_query.fetchall()]

        else:
            vals = (
                apps.get_model(
                    app_label="primo",
                    model_name=current_table.capitalize(),
                )
                .objects.values(
                    "variable_name",
                    "label",
                    "bodypart_variable__bodypart_id",
                )
                .all()
            )

    elif current_table == "bodypart" or current_table == "taxon":
        vals = []
        # Do original query to get root of tree.
        # The rest of the tree will be recursively created in
        # `create_tree_javascript()`.
        value = (
            apps.get_model(
                app_label="primo",
                model_name=current_table.capitalize(),
            )
            .objects.values(
                "id",
                "label",
                "parent_id",
                "expand_in_tree",
                "tree_root",
            )
            .filter(tree_root=1)[0]
        )

        name = value["label"].replace('"', "")
        item_id = value["id"]
        parent_id = value["parent_id"]
        expand = "true" if value["expand_in_tree"] else "false"
        javascript = (
            f'tree.add("{item_id}", "{parent_id}", "{name}", "", "", {expand}, '
        )
        if item_id not in request.session["table_var_select_done"][current_table]:
            javascript += "false );\n"
        else:
            javascript += "true );\n"

        # Now do follow-up query using root as parent.
        javascript += create_tree_javascript(request, item_id, current_table)

    elif current_table == "fossil" or current_table == "sex":
        current_model = apps.get_model(
            app_label="primo",
            model_name=current_table.capitalize(),
        )
    else:
        # I have to do the set because nlsTree seems to be forcing a
        # refresh with current_table set to "undefined". The actual
        # value is unimportant, so I've just chosen one that has a model.
        current_model = apps.get_model(
            app_label="primo",
            model_name="Taxon",
        )

        vals = current_model.objects.values("id", "label").all()

    return render(
        request,
        "primo/parameter_selection.jinja",
        {
            "current_table": current_table,
            "values": vals,
            "javascript": javascript,
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
            # Otherwise, "cancel" or "select all" was chosen.
            selected_rows: list[int] = []

            if (
                request.POST.get("table") == "taxon"
                or request.POST.get("table") == "bodypart"
            ):
                # I have to look at all POST variables and remove those that
                # start with 'cb_main', as those are set by nlstree.js.
                #
                # All selected items cause one 'cb_main' variable to be set,
                # as such: cb_main423 = 'on'. So I need to get the number at
                # the end, as that's the id of the selected item.
                for item in request.POST.items():
                    if item[0].startswith("cb_main"):
                        selected_rows.append(int(item[0][7:]))

                if request.POST.get("table") == "bodypart":
                    request.session["table_var_select_done"]["variable"] = []

            else:  # Return is *not* from nlstree.js, so can just get id values.
                for item in request.POST.getlist("id"):  # type: ignore
                    # Because .get() returns only last item. Note that getlist()
                    # returns an empty list for any missing key.
                    selected_rows.append(int(item))  # type: ignore
            request.session["table_var_select_done"][current_table] = selected_rows
    if not request.session["tables"] or request.session["scalar_or_3d"] != scalar_or_3d:
        # If tables isn't set, query for all tables and set up both tables and
        # selected lists. Note that "tables" will exist as key either way.
        # Note for this query that "tables" is set as the related name in Models.py.
        request.session["scalar_or_3d"] = scalar_or_3d
        tables = QueryWizardQuery.objects.get(
            data_table=scalar_or_3d.capitalize()
        ).tables.all()
        """selected will hold all preselected data (e.g. sex: [1, 2, 3, 4, 5, 9])."""
        selected = dict()
        request.session["tables"] = []
        request.session["table_var_select_done"] = dict()

        for table in tables:
            # if len(request.session['selected'][table.table_name]) == 0:
            request.session["tables"].append(
                {
                    "table_name": table.filter_table_name,
                    "display_name": table.display_name,
                }
            )

            if table.preselected:
                model = apps.get_model(
                    app_label="primo",
                    model_name=table.filter_table_name.capitalize(),  # type: ignore
                )
                values = model.objects.values("id").all()
                # Because vals is a list of dicts in format 'id': value.
                request.session["table_var_select_done"][table.filter_table_name] = [
                    value["id"] for value in values
                ]  # type: ignore
            else:
                request.session["table_var_select_done"][table.filter_table_name] = []
                # So I can use 'if selected[table]' in initialize_query.jinja.

    selected = request.session["table_var_select_done"]
    # I coudn't figure out any way to do this other than to check each time.
    finished = True

    for table in request.session["tables"]:
        if not selected[table["table_name"]]:  # type: ignore
            finished = False

    request.session.modified = True
    return render(
        request,
        "primo/initialize_query.jinja",
        {
            "scalar_or_3d": scalar_or_3d,
            "tables": request.session["tables"],
            "selected": selected,
            "finished": finished,
        },
    )


def execute_query(
    request: HttpRequest, scalar_or_3d: str
) -> Tuple[str, List[Dict[Any, Any]]]:
    """Set up the query SQL. Do query. Call result table display."""
    submission_values = [
        request.session["table_var_select_done"]["sex"],
        request.session["table_var_select_done"]["fossil"],
        request.session["table_var_select_done"]["taxon"],
    ]
    if scalar_or_3d.lower() == "scalar":
        sql_query = set_up_sql_query(True, True)
        submission_values.append(request.session["table_var_select_done"]["variable"])
        # We have to query for the variable names separately.
        with connection.cursor() as variable_query:
            # Recall that variable label is abbreviation, name is full name.
            variable_query.execute(
                "SELECT label  "
                "  FROM variable "
                " WHERE variable.id "
                "    IN %s "
                "ORDER BY label ASC;",
                [request.session["table_var_select_done"]["variable"]],
            )
            request.session["variable_labels"] = [
                label[0] for label in variable_query.fetchall()
            ]
    else:
        sql_query = set_up_sql_query(False, True)

    # Use cursor here?
    with connection.cursor() as cursor:
        cursor.execute(
            sql_query,
            submission_values,
        )
        # Now return all rows as a dictionary object. Note that each variable
        # name will have its own row, so I'm going to have to jump through some
        # hoops to get the names out correctly for the table headers in the view.
        # TODO: There has to be a better way to do this.

        columns = [col[0] for col in cursor.description]
        [dict(zip(columns, row)) for row in cursor.fetchall()]

    preview_only = True
    if request.user.is_authenticated and request.user.username != "user":
        preview_only = False

    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Consider moving all of this, and 3D into db. As it was before, dammit.
    sql_query = set_up_sql_query(True, preview_only)

    # We have to query for the variable names separately.
    with connection.cursor() as variable_query:
        variable_query.execute(
            "SELECT label "
            "  FROM variable "
            " WHERE variable.id "
            "    IN %s "
            "ORDER BY label ASC;",
            [request.session["table_var_select_done"]["variable"]],
        )
        [label[0] for label in variable_query.fetchall()]

    # Use cursor here?
    with connection.cursor() as cursor:
        cursor.execute(
            sql_query,
            [
                request.session["table_var_select_done"]["sex"],
                request.session["table_var_select_done"]["fossil"],
                request.session["table_var_select_done"]["taxon"],
                request.session["table_var_select_done"]["variable"],
            ],
        )
        # Now return all rows as a dictionary object. Note that each variable
        # name will have its own row, so I'm going to have to jump through some
        # hoops to get the names out correctly for the table headers in the view.
        # TODO: There has to be a better way to do this.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        return sql_query, [dict(zip(columns, row)) for row in cursor.fetchall()]


def preview(request: HttpRequest) -> HttpResponse:
    """Set up the scalar query SQL. Do query. Call result table display."""
    request.session["page_title"] = f"{request.session['scalar_or_3d']} Results Preview"

    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Consider moving all of this, and 3D into db. As it was before, dammit.

    sql_query, query_results = execute_query(request, request.session["scalar_or_3d"])

    are_results = True
    if request.session["scalar_or_3d"].lower() == "scalar":
        tabulated_query_results = []
        try:
            tabulated_query_results = tabulate_scalar(query_results, True)
            # request.session["query_results"] = tabulated_query_results
        except Exception:
            print(exc_info()[0])
            are_results = False
    # This is for use in export_csv_file().
    submission_values = [
        request.session["table_var_select_done"]["sex"],
        request.session["table_var_select_done"]["fossil"],
        request.session["table_var_select_done"]["taxon"],
    ]
    if request.session["scalar_or_3d"].lower() == "scalar":
        submission_values.append(request.session["table_var_select_done"]["variable"])
    context = {
        "final_sql": sql_query.replace("%s", "{}").format(*submission_values),
        "are_results": are_results,
        "total_specimens": len(tabulated_query_results),
        "preview_only": request.user.username == "user",
        "specimen_metadata": get_specimen_metadata(request.session["scalar_or_3d"]),
        "user": request.user.username,
        "query_results": tabulated_query_results,
    }
    if request.session["scalar_or_3d"].lower() == "scalar":
        context["variable_labels"] = request.session["variable_labels"]
        context["variable_ids"] = request.session["table_var_select_done"]["variable"]
        context["query_results"] = tabulated_query_results
        context["total_specimens"] = len(tabulated_query_results)
    else:
        # This is a list of all the session that will be returned from the query
        # so I can send it to `get_3D_data()` for a second query to get the actual data.
        # I'm using a set because each point is its own line in the output. A list
        # would have repeated data.
        sessions = set()
        for item in query_results:
            sessions.add(item["session_id"])
    return render(request, "primo/preview.jinja", context)


@login_required
def query_start(request: HttpRequest) -> HttpResponse:
    """Start or reset query by creating or emptying data structures."""
    request.session["page_title"] = "Query Wizard"
    request.session["tables"] = []
    request.session["selected"] = dict()
    request.session["selected"]["table"] = []
    request.session["scalar_or_3d"] = ""
    request.session["variable_labels"] = []
    # request.session['query_results'] = []
    return render(request, "primo/query_start.jinja")


def set_up_sql_query(is_scalar: bool, preview_only: bool) -> str:
    """Create an SQL query for either 3D or scalar data."""

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    # TODO: maybe move this back into the DB?
    # Note we skip variables in 3D SELECT: we're getting all of them.
    select_common = " ".join(
        [
            "specimen.id AS specimen_id,",
            "specimen.hypocode AS hypocode,",
            "session.id AS session_id,",
            "institute.abbr AS collection_acronym,",
            "specimen.catalog_number AS catalog_number,",
            "taxon.label AS taxon_label,",
            "specimen.mass AS mass,",
            "sex.sex AS sex_type,",
            "taxonomic_type.taxonomic_type,",
            "fossil.fossil_or_extant,",
            "captive.captive_or_wild,",
            "original.original_or_cast,",
            "age_class.age_class,",
            "locality.locality_name,",
            "country.country_name,",
            "specimen.comments AS specimen_comments,",
            "session.comments AS session_comments,",
            "observer.researcher_name AS researcher_name",
        ]
    )
    where = "WHERE sex.id IN %s AND fossil.id IN %s AND taxon.id IN %s"

    if is_scalar:
        select_start = (
            "SELECT data_scalar.id AS scalar_id, "
            "       variable.label AS variable_label, "
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
            "JOIN taxonomic_type",
            "  ON taxonomic_type.id = specimen.taxonomic_type_id",
            "JOIN age_class",
            "  ON age_class.id = specimen.age_class_id",
            "JOIN locality",
            "  ON locality.id = specimen.locality_id",
            "JOIN country",
            "  ON country.id = locality.country_id",
            "JOIN observer",
            "  ON observer.id = session.observer_id",
        ]
    )

    ordering = "ORDER BY `specimen_id` ASC"
    return f"{select_start} {select_common} {from_start} {joins} {where} {ordering};"


# def query_3d(request: HttpRequest, output_file_type: str) -> HttpResponse:
#     """
#     Set up the 3D query SQL. Do query for metadata. Call get_3D_data to get 3D
#     points. Send results to either Morphologika or GRFND creator and downloader.
#     If preview_only, ignore which_output_type and show metadata preview for top
#     five taxa.
#     Is this used?
#     """

#     preview_only = False
#     if not request.user.is_authenticated or request.user.username == "user":
#         preview_only = True

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
#         "groups": request.user.get_group_permissions(),
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
#         # return render(request, 'primo/download_success.jinja')

#     return render(request, "primo/preview.jinja", context)


def set_up_download(request: HttpRequest) -> Tuple[str, str]:
    """
    Set the newline character, set name of file based on current time.
    Put both in session variable. If it's 3D make 3D output directory.
    """

    # Stupid Windows: we need to make sure the newline is set correctly.
    # Abundance of caution.
    newline_char = "\n"
    if request.META["HTTP_USER_AGENT"].lower().find("win"):
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

    All requested variables
    """
    current_specimen = query_results[0]["hypocode"]
    output = []
    current_dict = init_query_table("Scalar", query_results[0])
    num_specimens = 1
    for row in query_results:
        # Is this a new specimen? If so need to set up new empty dictionary and
        # append it.
        if row["hypocode"] == current_specimen:
            current_dict[row["variable_label"]] = row["scalar_value"]
        else:
            num_specimens += 1
            output.append(current_dict)
            current_dict = init_query_table("Scalar", row)
            # This next so we can look up values quickly in view rather than
            # having to do constant conditionals.
            current_dict[row["variable_label"]] = row["scalar_value"]
            current_specimen = row["hypocode"]
        # TODO: Figure out SQL so we don't have to do entire query and cull it here.
        if preview_only and num_specimens >= 15:
            break
    output.append(current_dict)
    return output
