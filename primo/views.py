import subprocess
from csv import DictWriter
from datetime import datetime
from os import mkdir, path
from sys import exc_info
from typing import Dict, Tuple

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


def collate_metadata(request: HttpRequest) -> None:
    """
    Collate data returned from SQL query, render into csv, save csv to tmp
    directory. For scalar write all data. For 3D write only metadata.
    """
    output_file_name = path.join(
        settings.DOWNLOAD_ROOT,
        request.session["directory_name"],
        request.session["file_to_download"],
    )
    with open(
        output_file_name,
        "w",
        newline="",
        # For some reason request.session['newline_char'] added a newline on each row
    ) as f:
        csv_file = File(f)
        meta_names = [m[0] for m in get_specimen_metadata(request)]
        if request.session["scalar_or_3d"] == "3D":
            meta_names.append("missing points (indexed by specimen starting at 1)")
            variable_names = []
        else:
            # variable_names = [ v[0] for v in request.session.keys() ]
            variable_names = request.session["variable_labels"]

        writer = DictWriter(csv_file, fieldnames=meta_names + variable_names)

        # This so I can replace default header, i.e. fieldnames, with custom header.
        # Note to self: since I'm using DictWriter I don't have to worry about
        # the ordering of the header being different from the order of the subsequent
        # rows: it takes care of that.
        row = {m[0]: m[1] for m in get_specimen_metadata(request)}
        # row.update( { v: v for v in request.session.keys() } )
        row.update({v: v for v in variable_names})
        writer.writerow(row)

        if request.session["scalar_or_3d"] == "3D":
            meta_names.append("missing points (indexed by specimen starting at 1)")
            rows = request.session["3d_metadata"]
        else:
            rows = request.session["query_results"]
        for row in rows:
            inDict = {
                k: row[k]
                for k in row.keys()
                if k != "scalar_value" and k != "variable_label"
            }
            if request.session["scalar_or_3d"] == "3D":
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
            "name",
            "parent_id",
            "expand_in_tree",
        )
        .filter(parent_id=parent_id)
    )
    for val in vals:
        # Remove quote marks from `name`, as they'll screw up Javascript
        name = val["name"].replace('"', "")
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


def download(request: HttpRequest) -> HttpResponse:
    """
    Download one of csv, Morphologika, GRFND. File has been written to path
    before this is called.
    """
    request.session[
        "page_title"
    ] = f"PRIMO Download {request.session['scalar_or_3d']} Data"
    if request.session["scalar_or_3d"] == "3D":
        filepath = path.join(settings.DOWNLOAD_ROOT, request.session["directory_name"])
    else:
        filepath = path.join(
            settings.DOWNLOAD_ROOT, request.session["file_to_download"]
        )

    if path.exists(filepath):
        if request.session["scalar_or_3d"] == "3D":
            # Just as a reminer, -c is create a new file; -z is gzip it;
            # -f is filename; -C is move to the following directory first;
            # name at end is the directory to compress.
            # Using -C here to get rid of prefix of absolute file path.
            # So: tar -czf DOWNLOAD_ROOT/filename.tar.gz -C DOWNLOAD_ROOT directory_name
            # Files should be in request.session['directory_name'], so that directory is
            # what needs to be compressed, meaning tar needs to operate from
            # DOWNLOAD_ROOT.
            subprocess.run(
                [
                    "tar",
                    "-czf",
                    path.join(
                        settings.DOWNLOAD_ROOT,
                        request.session["directory_name"] + ".tar.gz",
                    ),
                    "-C",
                    settings.DOWNLOAD_ROOT,
                    request.session["directory_name"],
                ]
            )
            # We have to reset filepath here because now we've tarred it.
            filepath = path.join(
                settings.DOWNLOAD_ROOT, request.session["directory_name"] + ".tar.gz"
            )
        with open(filepath, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response["Content-Disposition"] = "inline; filename=%s" % smart_str(
                path.basename(request.session["file_to_download"])
            )
            response["X-Sendfile"] = smart_str(filepath)
            return response
    raise Http404


def download_success(request: HttpRequest) -> HttpResponse:
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


def export_scalar(request: HttpRequest) -> HttpResponse:
    request.session["scalar_or_3d"] = "scalar"
    set_up_download(request)
    collate_metadata(request)
    return download(request)


def export_3d(request: HttpRequest) -> HttpResponse:
    #     request.session["which_3d_output_type"] = which_3d_output_type
    request.session["scalar_or_3d"] = "3D"
    set_up_download(request)
    create_3d_output_string(request)
    collate_metadata(request)
    return download(request)


def create_3d_output_string(request: HttpRequest) -> None:
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
    num_query_results = len(request.session["query_results"])
    num_sessions = len(request.session["sessions"])
    if request.session["which_3d_output_type"] == "Morphologika":
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

    for row in request.session["query_results"]:
        output_str += f"{row['specimen_id']}{newline_char}"
    # data points
    if request.session["which_3d_output_type"] == "Morphologika":
        output_str += f"{newline_char}[rawpoints]{newline_char}"
    """
    point_ctr will be used to track which points are missing for a given
    sessiom/specimen.
    """
    missing_point_ctr = 1
    current_specimen = -1  # Keeps track of when new specimen data starts.
    for row in request.session["query_results"]:
        if row["specimen_id"] != current_specimen:
            current_specimen = row["specimen_id"]
            if request.session["which_3d_output_type"] == "Morphologika":
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


def fixQuotes(inStr: str) -> str:
    """Quote all the things that need to be quoted in a csv row."""

    needQuote = False

    # -----------------------------------------------------------------
    #  Quotes in the value must be escaped.
    # -----------------------------------------------------------------
    if inStr.find('"') >= 0:
        inStr = inStr.replace('"', '""')
        needQuote = True

    # -----------------------------------------------------------------
    #  The value separater must be quoted ("," in this case.)
    # -----------------------------------------------------------------
    elif inStr.find(",") >= 0:
        needQuote = True

    # -----------------------------------------------------------------
    #  Quote line breaks if they are present.
    # -----------------------------------------------------------------
    elif (inStr.find("\n") >= 0) or (inStr.find("\r") >= 0):  # \r is for Mac
        needQuote = True

    # -----------------------------------------------------------------
    #  Quote equal sign (Excel interprets this as a formula).
    # -----------------------------------------------------------------
    elif inStr.find("=") >= 0:
        needQuote = True

    if needQuote:
        inStr = '"' + inStr + '"'

    return inStr


def get_3D_data(request: HttpRequest) -> None:
    """Execute query for actual 3D points, i.e. not metadata."""

    base = (
        "SELECT DISTINCT session.id AS session_id, "
        "                specimen.id AS specimen_id, "
        "                specimen.hypocode AS hypocode, "
        "                data_3d.x, "
        "                data_3d.y, "
        "                data_3d.z, "
        "                data_3d.datindex, "
        "                data_3d.variable_id "
        "FROM data_3d "
        "     JOIN variable ON data_3d.variable_id = variable.id "
        "     JOIN session ON data_3d.session_id = session.id "
        "     JOIN specimen ON session.specimen_id = specimen.id"
    )

    where = " WHERE session_id IN %s"
    group_by = " GROUP BY session_id"
    ordering = " ORDER BY specimen_id, variable_id, data_3d.datindex ASC"
    final_sql = base + where + ordering + group_by + ";"

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
    request.session["query_results"] = query_results


def get_specimen_metadata(request: HttpRequest) -> list[Tuple[str, str]]:
    """
    Return a list of tuples with SQL column name:csv column name as key:value.
    Created a fn because this was called all over the place.
    """

    if request.session["scalar_or_3d"] == "3D":
        three_d_list = [
            ("protocol", "Protocol"),
            ("session_id", "Session ID"),
            ("missing_pts", "Missing points (indexed by specimen starting at 1)"),
        ]
    else:
        three_d_list = []
    return [
        ("specimen_id", "Specimen ID"),
        ("hypocode", "Hypocode"),
        ("collection_acronym", "Collection Acronym"),
        ("catalog_number", "Catalog No."),
        ("taxon_name", "Taxon name"),
        ("sex_type", "Sex"),
        ("specimen_type", "Type Status"),
        ("mass", "Mass"),
        ("fossil_or_extant", "Fossil or Extant"),
        ("captive_or_wild", "Captive or Wild"),
        ("original_or_cast", "Original or Cast"),
        ("session_comments", "Session Comments"),
        ("specimen_comments", "Specimen Comments"),
        ("age_class", "Age Class"),
        ("locality_name", "Locality"),
        ("country_name", "Country"),
    ] + three_d_list


def init_query_table(
    request: HttpRequest, query_result: Dict[str, str]
) -> Dict[str, str]:
    """
    Initialize query table (actually a dictionary) that is to be used for data
    that will be pushed out to view. A single query row is received and put into
    dictionary.
    """
    output = {key[0]: query_result[key[0]] for key in get_specimen_metadata(request)}
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
    javascript = ""
    request.session["page_title"] = f"{current_table.capitalize()} Selection"
    if current_table == "variable":
        if request.session["table_var_select_done"]["bodypart"]:
            with connection.cursor() as variable_query:
                sql = (
                    "SELECT variable.name AS var_name, "
                    "       variable.label AS var_label, "
                    "       variable.id AS var_id, "
                    "       bps.id AS bodypart_id, "
                    "       bps.name AS bodypart_name "
                    "FROM variable "
                    "    JOIN bodypart_variable "
                    "         ON variable.id = bodypart_variable.variable_id "
                    "    JOIN (SELECT bodypart.id, bodypart.name "
                    "            FROM bodypart "
                    "           WHERE id IN %s) AS bps "
                    "      ON bps.id = bodypart_variable.bodypart_id "
                    "ORDER BY variable.id"
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
                    "name",
                    "label",
                    "bodypartvariable__bodypart_id",
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
                "name",
                "parent_id",
                "expand_in_tree",
                "tree_root",
            )
            .filter(tree_root=1)[0]
        )

        name = value["name"].replace('"', "")
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

        vals = current_model.objects.values("id", "name").all()

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
def query_setup(request: HttpRequest, scalar_or_3d: str = "scalar") -> HttpResponse:
    """
    For scalar queries send parameter_selection to frontend. Once all
    parameters are set, give option to call results, e.g. query_scalar().

    Tables will be all of the tables that are available to search on for a
    particular search type (e.g. scalar or 3D). Of those tables sex and
    fossil will be pre-filled with all values selected. In that case,
    do a second query for all possible values and fill those values in.
    """
    request.session["page_title"] = f"{scalar_or_3d.title()} Query Wizard"
    if request.method == "POST":
        # If there's a POST, then parameter_selection has been called and some
        # values have been sent back.
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
    if not request.session["tables"]:
        # If tables isn't set, query for all tables and set up both tables and
        # selected lists. Note that "tables" will exist as key either way.
        request.session["scalar_or_3d"] = scalar_or_3d

        # Note for this query that "tables" is set as the related name in Models.py.
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
                # So I can use 'if selected[table]' in query_setup.jinja.

    selected = request.session["table_var_select_done"]
    # I coudn't figure out any way to do this other than to check each time.
    finished = True

    for table in request.session["tables"]:
        if not selected[table["table_name"]]:  # type: ignore
            finished = False

    request.session.modified = True
    return render(
        request,
        "primo/query_setup.jinja",
        {
            "scalar_or_3d": scalar_or_3d,
            "tables": request.session["tables"],
            "selected": selected,
            "finished": finished,
        },
    )


def query_scalar(request: HttpRequest) -> HttpResponse:
    """Set up the scalar query SQL. Do query. Call result table display."""
    request.session["page_title"] = "Scalar Results"
    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Consider moving all of this, and 3D into db. As it was before, dammit.
    request.session["scalar_or_3d"] = "scalar"
    preview_only = True
    if request.user.is_authenticated and request.user.username != "user":
        preview_only = False

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    # TODO: move this back into the DB.
    base = (
        "SELECT data_scalar.id AS scalar_id, "
        "       specimen.id AS specimen_id, "
        "       specimen.hypocode AS hypocode, "
        "       institute.abbr AS collection_acronym, "
        "       specimen.catalog_number AS catalog_number, "
        "       taxon.name AS taxon_name, "
        "       specimen.mass AS mass, "
        "       sex.name AS sex_type, "
        "       specimen_type.name AS specimen_type, "
        "       fossil.name AS fossil_or_extant, "
        "       captive.name AS captive_or_wild, "
        "       original.name AS original_or_cast, "
        "       variable.label AS variable_label, "
        "       data_scalar.value AS scalar_value, "
        "       age_class.name AS age_class, "
        "       locality.name AS locality_name, "
        "       country.name AS country_name, "
        "       specimen.comments AS specimen_comments, "
        "       session.comments AS session_comments "
        "FROM variable "
        "     JOIN data_scalar"
        "          ON data_scalar.variable_id = variable.id "
        "     JOIN session "
        "          ON data_scalar.session_id = session.id "
        "     JOIN specimen "
        "          ON session.specimen_id = specimen.id "
        "     JOIN original "
        "          ON session.original_id = original.id "
        "     JOIN taxon "
        "          ON specimen.taxon_id = taxon.id "
        "     JOIN sex "
        "          ON specimen.sex_id = sex.id "
        "     JOIN fossil "
        "          ON specimen.fossil_id = fossil.id "
        "     JOIN institute "
        "          ON specimen.institute_id = institute.id "
        "     JOIN captive "
        "          ON specimen.captive_id = captive.id "
        "     JOIN specimen_type "
        "          ON specimen.specimen_type_id = specimen_type.id "
        "     JOIN age_class "
        "          ON specimen.age_class_id = age_class.id "
        "     JOIN locality "
        "          ON specimen.locality_id = locality.id "
        "     JOIN country "
        "          ON locality.country_id = country.id"
    )

    where = (
        " WHERE sex.id IN %s "
        "AND fossil.id IN %s "
        "AND taxon.id IN %s "
        "AND variable.id IN %s "
    )
    ordering = " ORDER BY specimen.id, variable.label ASC"
    final_sql = f"{base} {where} {ordering};"

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
        variable_labels = [label[0] for label in variable_query.fetchall()]

    # Use cursor here?
    with connection.cursor() as cursor:
        cursor.execute(
            final_sql,
            [
                request.session["table_var_select_done"]["sex"],
                request.session["table_var_select_done"]["fossil"],
                request.session["table_var_select_done"]["taxon"],
                # concat_variable_list(request.session['selected']['bodypart']),
                request.session["table_var_select_done"]["variable"],
            ],
        )
        # Now return all rows as a dictionary object. Note that each variable
        # name will have its own row, so I'm going to have to jump through some
        # hoops to get the names out correctly for the table headers in the view.
        # TODO: There has to be a better way to do this.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    are_results = True
    try:
        new_query_results = tabulate_scalar(request, query_results, preview_only)
        request.session["query_results"] = new_query_results
    except Exception:
        print(exc_info()[0])
        are_results = False

    # This is for use in export_csv_file().
    request.session["variable_labels"] = variable_labels
    context = {
        "final_sql": final_sql.replace("%s", "{}").format(
            request.session["table_var_select_done"]["sex"],
            request.session["table_var_select_done"]["fossil"],
            request.session["table_var_select_done"]["taxon"],
            # concat_variable_list(request.session['selected']['bodypart']),
            request.session["table_var_select_done"]["variable"],
        ),
        "query_results": new_query_results,
        "are_results": are_results,
        "total_specimens": len(new_query_results),
        "variable_labels": variable_labels,
        "variable_ids": request.session["table_var_select_done"]["variable"],
        "preview_only": preview_only,
        "specimen_metadata": get_specimen_metadata(request),
        "user": request.user.username,
    }
    return render(request, "primo/query_results.jinja", context)


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


def query_3d(
    request: HttpRequest, which_3d_output_type: str, preview_only: bool
) -> HttpResponse:
    """
    Set up the 3D query SQL. Do query for metadata. Call get_3D_data to get 3D points.
    Send results to either Morphologika or GRFND creator and downloader.
    If preview_only, ignore which_output_type and show metadata preview for top
    five taxa.
    """

    if not request.user.is_authenticated or request.user.username == "user":
        preview_only = True

    request.session["scalar_or_3d"] = "3D"
    request.session["which_3d_output_type"] = which_3d_output_type
    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Move all of this and 3D into db. As it was before, dammit.

    # This is for cleaner code when composing header row for metadata csv.
    # First value is field name in DB, second is header name for metadata csv.

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    # We'll only do metadata search first.

    # Note
    base = (
        "SELECT DISTINCT specimen.id AS specimen_id, "
        "                specimen.hypocode AS hypocode, "
        "                institute.abbr AS collection_acronym, "
        "                specimen.catalog_number AS catalog_number, "
        "                taxon.name AS taxon_name, "
        "                specimen.mass AS mass, "
        "                sex.name AS sex_type, "
        "                specimen_type.name AS specimen_type, "
        "                fossil.name AS fossil_or_extant, "
        "                captive.name AS captive_or_wild, "
        "                original.name AS original_or_cast, "
        "                protocol.label AS protocol, "
        "                age_class.name AS age_class, "
        "                locality.name AS locality_name, "
        "                country.name AS country_name, "
        "                session.comments AS session_comments, "
        "                session.id AS session_id, "
        "                specimen.comments AS specimen_comments "
        "FROM data_3d "
        "     JOIN `session` "
        "       ON data_3d.session_id = session.id "
        "     JOIN `specimen` "
        "       ON session.specimen_id = specimen.id "
        "     JOIN `taxon` "
        "       ON specimen.taxon_id = taxon.id "
        "     JOIN `sex` "
        "       ON specimen.sex_id = sex.id "
        "     JOIN `specimen_type` "
        "       ON specimen.specimen_type_id = specimen_type.id "
        "     JOIN `fossil` "
        "       ON specimen.fossil_id = fossil.id "
        "     JOIN `institute` "
        "       ON specimen.institute_id = institute.id "
        "     JOIN `protocol` "
        "       ON session.protocol_id = protocol.id "
        "     JOIN `captive` "
        "       ON specimen.captive_id = captive.id "
        "     JOIN `original` "
        "       ON session.original_id = original.id "
        "     JOIN `age_class` "
        "       ON specimen.age_class_id = age_class.id "
        "     JOIN `locality` "
        "       ON specimen.locality_id = locality.id "
        "     JOIN `country` "
        "       ON locality.country_id = country.id "
    )

    where = " WHERE `sex`.`id` IN %s AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s"
    ordering = " ORDER BY `specimen_id` ASC"
    limit = ""
    if preview_only:  # TODO: This could be a little more nicer.
        limit = " LIMIT 5"
    final_sql = base + where + ordering + limit + ";"

    # We skip variables in 3D: we're getting all of them.

    # This is a list of all the session that will be returned from the query
    # so I can send it to `get_3D_data()` for a second query to get the actual data.
    # I'm using a set because each point is it's own line in the output. A list
    # would have repeated data.
    sessions = set()

    with connection.cursor() as cursor:
        cursor.execute(
            final_sql,
            [
                request.session["table_var_select_done"]["sex"],
                request.session["table_var_select_done"]["fossil"],
                request.session["table_var_select_done"]["taxon"],
            ],
        )
        # Now return all rows as a dictionary object. Note that each variable
        # name will have its own row, so I'm going to have to jump through some
        # hoops to get the names out correctly for the table headers in the view.

        # TODO: There has to be a better way to do that.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # Need to get session ids in case file will be downloaded.
        # Single specimen per session is enforced at DB level.
        # This won't be used for preview.
        for item in query_results:
            sessions.add(item["session_id"])

    request.session["query"] = final_sql
    request.session["sessions"] = list(sessions)
    request.session["3d_metadata"] = query_results

    context = {
        "final_sql": final_sql.replace("%s", "{}")
        .format(
            request.session["table_var_select_done"]["sex"],
            request.session["table_var_select_done"]["fossil"],
            request.session["table_var_select_done"]["taxon"],
        )
        .replace("[", "(")
        .replace("]", ")"),
        "groups": request.user.get_group_permissions(),
        "preview_only": preview_only,
        "query_results": query_results,
        "scalar_or_3d": request.session["scalar_or_3d"],
        "specimen_metadata": get_specimen_metadata(request),
        "total_specimens": len(
            query_results
        ),  # This should be the same as len(request.session['sessions'])
        "user": request.user.username,
    }

    # If it's not a preview I need to get actual data and then send to Morphologika
    # or GRFND.
    if not preview_only:
        get_3D_data(request)
        export_3d(request)
        # return render(request, 'primo/download_success.jinja')

    return render(request, "primo/query_results.jinja", context)


def set_up_download(request: HttpRequest) -> None:
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
    request.session["file_to_download"] = (
        prefix + datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".csv"
    )
    directory_name = ""
    if request.session["scalar_or_3d"] == "3D":
        directory_name = "PRIMO_3D_" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        request.session["file_to_download"] = "specimen_metadata.csv"
        mkdir(path.join(settings.DOWNLOAD_ROOT, directory_name))

    request.session["directory_name"] = directory_name


def tabulate_scalar(
    request: HttpRequest, query_results: list[dict[str, str]], preview_only: bool
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
    current_dict = init_query_table(request, query_results[0])
    num_specimens = 1
    for row in query_results:
        # Is this a new specimen? If so need to set up new empty dictionary and
        # append it.
        if row["hypocode"] == current_specimen:
            current_dict[row["variable_label"]] = row["scalar_value"]
        else:
            num_specimens += 1
            output.append(current_dict)
            # TODO: do I need this del here?
            del current_dict
            current_dict = init_query_table(request, row)
            # This next so we can look up values quickly in view rather than having
            # to do constant conditionals.
            current_dict[row["variable_label"]] = row["scalar_value"]
            current_specimen = row["hypocode"]
        # TODO: Figure out SQL so we don't have to do entire query and cull it here.
        if preview_only and num_specimens >= 15:
            break
    output.append(current_dict)
    return output
