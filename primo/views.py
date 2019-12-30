from .forms                         import *
from .models                        import *
from django.apps                    import apps
from django.conf                    import settings
from django.contrib.auth            import authenticate, login, logout
from django.contrib.auth.models     import User
from django.contrib.auth.decorators import login_required
from django.core.files              import File
from django.core.mail               import send_mail
from django.db                      import connection
from django.http                    import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts               import get_object_or_404, redirect, render, render_to_response
from django.urls                    import reverse
from django.utils                   import timezone
from django.utils.encoding          import smart_str
from django.views.generic           import TemplateView

from csv                            import DictWriter
from datetime                       import datetime
from functools                      import reduce
from os                             import mkdir, path, remove
from uuid                           import uuid1


# Create your views here.

# def index(request):
#     return render(request, 'frontend/index.html')

class IndexView(TemplateView):
    """ docstring for IndexView """
    template_name = 'primo/index.jinja'


def concatVariableList(myList):
    """ Return myList as comma-seperated string of values enclosed in parens. """
    return '(' + reduce((lambda b,c : b + str(c) + ','), myList, '' )[:-1] + ')'


def create_tree_javascript(request, parent_id, current_table):
    """ Create javascript for heirarchical tree display. Formal parameters for
        tree.add() are:
        add(node_id, parent_id, node name, url, icon, expand?, precheck?, extra info,
        text on mouse hover).
        The last two are currently unneeded, and therefore ignored below.
        Function is recursive on parent_id and returns a properly-formatted string
        of Javascript code, although from reading nlstree docs (https://www.addobject.com/nlstree),
        it seems order is unimportant, so recursion may be unnecessary (wasteful?).
        Oh, wait: necessary because of if statement dealing with Eucatarrhini.
        Okay, so *eventually* unnecessary? """
    javascript = ''
    js_item_delimiter = '", "'

    vals = apps.get_model( app_label  = 'primo',
                           model_name = current_table.capitalize()
                         ).objects.values( 'id',
                                           'name',
                                           'parent_id',
                                           'expand_in_tree',
                                         ).filter(parent_id = parent_id)
    #print(vals)
    for val in vals:
        # remove quote marks from `name`, as they'll screw up Javascript
        name      = val['name'].replace('"', '')
        item_id   = val['id']
        parent_id = val['parent_id']
        expand    = 'true' if val['expand_in_tree'] else 'false'
        #print(name)
        if name != 'Eocatarrhini': # I'm not clear why I don't need to recurse up Eucatarrhini heirarchy.
                                   # Note that there's an extra blank entry for icon after the second item_id.
            javascript += 'tree.add("' \
                        + str(item_id)   + js_item_delimiter \
                        + str(parent_id) + js_item_delimiter \
                        + name           + js_item_delimiter \
                        + str(item_id)   + js_item_delimiter + '", ' \
                        + expand + ', '

            javascript += 'false );\n' if item_id not in request.session['selected'][current_table] else 'true );\n'
            javascript += create_tree_javascript(request, item_id, current_table)

    return javascript


def download(request):
    """ Download one of csv, morphologika, grfnd. File has been written to path before this is called. """
    filepath = path.join(settings.DOWNLOAD_ROOT, request.session['file_to_download'])
    if path.exists(filepath):
        with open(filepath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=%s' % smart_str(path.basename(request.session['file_to_download']))
            response['X-Sendfile'] = smart_str(filepath)
            return response
    raise Http404


def downloadSuccess(request):
    return render(request, 'primo/download_success.jinja', {})


def email(request):
    """ Create email form, collect info, send email. """
    form = EmailForm(request.POST or None)

    success = False
    error   = None
    if request.method == 'POST':
        if form.is_valid():
            # get crap from POST
            name  = request.POST.get('first_name') + ',' + request.POST.get('last_name')
            email = request.POST.get('email') + ','
            body  = name + ',' + email + ','
            body += request.POST.get('affiliation') + ','
            body += request.POST.get('position') + ','
            body += request.POST.get('dept') + ','
            body += request.POST.get('institute') + ','
            body += request.POST.get('country') + ','
            body += request.POST.get('body')

            # send email
            # error   = send_mail('PRIMO password request', body, email, ['ericford@mac.com'], fail_silently=False)
            # success = True
            return render(request, 'primo/email.jinja', {'success': True, 'error': error})
        # form is not valid, so errors should print
        return render(request, 'primo/email.jinja', {'form': form})
    # There is no POST data, page hasn't loaded previously,
    return render(request, 'primo/email.jinja', {'form': form})


def erd(request):
    """ Retrieve relational database table pdf. """
    return render(request, 'primo/entity_relation_diagram.jinja')


def export_2d(request):
    request.session['3d'] = False
    setUpDownload(request)
    collateMetadata(request)
    return download(request)



def collateMetadata(request):
    """ Collate data returned from SQL query, render into csv, save csv to tmp directory,
        start download.
        This is for 2D data. For 3D data we write either or Morphologika or GRFND file. """

    with open( path.join( settings.DOWNLOAD_ROOT,
                          request.session['file_to_download'],
                        ),
               'w',
               newline=request.session['newlineChar'],
             ) as f:
        csvfile = File(f)
        meta_names = [ m[0] for m in get_specimen_metadata() ]
        if request.session['3d']:
            meta_names.append('missing points (indexed by specimen starting at 1)')
            variable_names = []
        else:
            var_names  = [ v[0] for v in request.session['variable_labels'] ]

        writer = DictWriter(csvfile, fieldnames=meta_names + var_names)

        # writer.writeheader()
        # This so I can replace default header, i.e. fieldnames, with custom header.
        # Note to self: since I'm using DictWriter I don't have to worry about the ordering of the header
        # being different from the order of the subsequent rows; it takes care of that.
        row = { m[0]: m[1] for m in get_specimen_metadata() }
        row.update( { v[0]: v[0] for v in request.session['variable_labels'] } )
        writer.writerow(row)
        for row in request.session['query_results']:
            inDict = { k : row[k] for k in row.keys() if k != 'scalar_value' and k != 'variable_label' }
            writer.writerow(inDict)


def exportMorphologika(request):
    """ Collate data returned from 3D SQL query.
        Print out two files: a csv of metadata and a Morphologika file. Fields included in metadata
        are enumerated below. """

    setUpDownload(request)
    request.session['3d'] = True
    retStr = request.session['newlineChar']

    missing_pts = {} # These will be output in metadata csv file.
                     # key is specimen id, value is list of missing points for specimen

    metaDataLen = len(get_specimen_metadata())

    # Morphologika file format:
    # [individuals]
    # number of individuals
    # [landmarks]
    # number of landmarks (total specimens/length of metadata)
    # [dimensions]
    # 3
    # [names]
    # specimen ids
    # [rawpoints]
    # datapoints as x \t y \t z (TODO: are these ordered)
    output_str =  (retStr * 2).join([ '[individuals]'
                                    , str(metaDataLen)
                                    , '[landmarks]'
                                    , str(request.session['total_specimens'] / metaDataLen)
                                    , '[dimensions]'
                                    , '3'
                                    , '[names]'
                                    ])
    # specimen ids
    for key, value in get_specimen_metadata():
        output_str += value['specimen_id'] + retStr

    # data points
    output_str += retStr + '[rawpoints]' + retStr
    cur_specimen = ''   # Keeps track of when new specimen data starts
    point_ctr = 1
    for key, value in values:
        if value['specimen_id'] != new_specimen:
            cur_specimen = value['specimen_id']
            output_str += retStr + "'" + value['hypocode'].replace('/ /', '_') + retStr
            point_ctr = 1
        if value['x'] == '9999.0000' and value['y'] == '9999.0000' and value['z'] == '9999.0000':
            output_str += '9999\t9999\t9999' + retStr
            if value['specimen_id'] not in missing_pts:
                missing_pts[ value['specimen_id'] ] = point_ctr;
            else:
                missing_pts[ value['specimen_id'] ] += ' ' + point_ctr;

        else:
            output_str += value['x'] + "\t" + value['y'] + "\t" + value['z'] + retStr

        point_ctr += 1

        dirName = 'PRIMO_3D_' + uuid1()  # uuid1() creates UUID string
        metadata_output_str = ''
        with open( path.join( settings.DOWNLOAD_ROOT,
                              request.session['file_to_download']
                            ),
                   'w',
                   newline=request.session['newlineChar']
                  ) as f:
            csvfile = File(f)

            outFile.write( ' specimen id, hypocode, institute, catalog number, taxon name, mass, sex, fossil or extant, captive or wild-caught, original or cast, protocol, session comments, specimen comments, missing points (indexed by specimen starting at 1)' + retStr )
            outFile.write( ', '.join(fieldNamesArray) )
            for key, value in metaData:
                for metaKey, metaValue in value: ## was    metaData[key]:
                    if metaKey != 'datindex' and metaKey != 'variable_id':
                        metadata_output_str += fixQuotes(metaVal) + ','
                try:
                    metadata_output_str += missing_pts[ value['specimen_id'] ]
                except:
                    pass

                metadata_output_str += retStr;

            outFile.write(metadata_output_str)
            outFile.close()

            # outFile = open('/tmp/' + dirName + '/3d_data.txt', 'w');
            # outFile.write(output_str)
            # outFile.close()
            # exec("tar -czf /tmp/$folderName.tar.gz /tmp/$folderName/");
            # unlink("/tmp/$folderName/3d_data.txt");
            # unlink("/tmp/$folderName/specimen_data.csv");
            # rmdir("/tmp/$folderName");

#             $file = file_get_contents ("/tmp/$folderName.tar.gz");
#             header("Content-type: application/x-compressed");
#             header('Content-disposition: gz; filename=PRIMO_3D_output_' + date("Y-m-d-H-i-s") + "_$which.tar.gz; size=".strlen($file));
#             echo $file;

#             unlink("/tmp/$folderName.tar.gz");
#         }


#         exit;
#     }
        # TODO: What did this use to do?
        # except:
        #     pass


def fixQuotes(inStr):
    """ Quote all the things that need to be quoted in a csv row. """

    needQuote = False;

    # -----------------------------------------------------------------
    #  Quotes in the value must be escaped.
    # -----------------------------------------------------------------
    if inStr.find('"') >= 0:
        inStr     = inStr.replace('"', '""')
        needQuote = True

    # -----------------------------------------------------------------
    #  The value separater must be quoted ("," in this case.)
    # -----------------------------------------------------------------
    elif inStr.find(",") >= 0:
        needQuote = True

    # -----------------------------------------------------------------
    #  Quote line breaks if they are present.
    # -----------------------------------------------------------------
    elif (inStr.find('\n') >= 0) or (inStr.find('\r') >= 0): # \r is for mac
        needQuote = True;

    # -----------------------------------------------------------------
    #  Quote equal sign (Excel interprets this as a formula).
    # -----------------------------------------------------------------
    elif inStr.find('=') >= 0:
        needQuote = True

    if (needQuote):
        inStr = '"' + inStr + '"'

    return inStr


def get3D_data(request):
    ''' Execute query for actual 3D points, i.e. not metadata. '''

    base = 'SELECT DISTINCT `session`  .`id` AS session_id, \
                            `specimen` .`id` AS specimen_id, \
                            `specimen` .`hypocode` AS `hypocode`, \
                            `data_3d`  .`x`, \
                            `data_3d`  .`y`, \
                            `data_3d`  .`z`, \
                            `data_3d`  .`datindex`, \
                            `data_3d`  .`variable_id` \
            FROM \
                data_3d \
            INNER JOIN `variable` ON `data_3d`.`variable_id` = `variable` .`id` \
            INNER JOIN `session`  ON `data_3d`.`session_id`  = `session`  .`id` \
            INNER JOIN `specimen` ON `session`.`specimen_id` = `specimen` .`id`'

    where     = ' WHERE `session_id` IN %s'
    ordering  = ' ORDER BY `specimen_id`, `variable_id`, `data_3d`.`datindex` ASC'
    final_sql = (base + where + ordering + ';')

    with connection.cursor() as cursor:
        cursor.execute( final_sql, [ request.session['sessions'] ]
                      )
        # Now return all rows as a dictionary object. Note that each variable name will have its own row,
        # so I'm going to have to jump through some hoops to get the names out correctly for the
        # table headers in the view. TODO: There has to be a better way to do that.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        query_results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    return



def init_query_table(query_result):
    """ Initialize query table (actually a dictionary) that is to be used for data
        that will be pushed out to view. A single query row is received and put into
        dictionary. """
    output = { key[0]: query_result[key[0]] for key in get_specimen_metadata() }
    output['variable_label'] = query_result['variable_label']
    output['scalar_value']   = query_result['scalar_value']
    return output


def log_in(request):
    form = LoginForm(request.POST or None)

    try:
        next_page = request.GET['next']
    except:
        next_page = '/'
    if request.method == 'POST' and form.is_valid():
        username  = request.POST.get('user_name')
        password  = request.POST.get('password')
        next_page = request.POST.get('next')
        user      = authenticate(username=username, password=password)

        if user is not None and user.is_active:
                login(request, user)
                return redirect(next_page)
        else:
            return render( request,
                          'primo/login.jinja',
                              { 'form': form,
                                'error': "Your username/password combination didn’t match. Please try again.",
                                'next': next_page
                              }
                         )
    else:
        return render(request, 'primo/login.jinja', {'form': form,
                                                     'next': next_page,
                                                     'error': None,
                                                    } )


@login_required
def logout_view(request):
    logout(request)
    return render(request, 'primo/logout.jinja')


@login_required
def parameter_selection(request, current_table):
    javascript = ''

    current_model = apps.get_model( app_label  = 'primo',
                                    model_name = current_table.capitalize(),
                                  )

    if current_table == 'variable':
        if len(request.session['selected']['bodypart']) > 0:
            bodypart_list         = request.session['selected']['bodypart']
            bodypart_variable_ids = current_model.objects.values('id').filter(bodypartvariable__bodypart_id__in=bodypart_list)
            variable_ids          = BodypartVariable.objects.values('variable_id').filter(pk__in=bodypart_variable_ids)
            vals                  = current_model.objects.values( 'id',
                                                                  'name',
                                                                  'label',
                                                                ).filter(pk__in=variable_ids).order_by('id')
        else:
            vals = apps.get_model( app_label  = 'primo',
                                   model_name = current_table.capitalize(),
                                 ).objects.values( 'name',
                                                   'label',
                                                   'bodypartvariable__bodypart_id',
                                                 ).all()

    elif current_table == 'bodypart' or current_table == 'taxon':
        vals = []
        # do original query to get root of tree.
        # The rest of the tree will be recursively created in `create_tree_javascript()`.
        val = apps.get_model( app_label  = 'primo',
                              model_name = current_table.capitalize(),
                            ).objects.values( 'id',
                                              'name',
                                              'parent_id',
                                              'expand_in_tree',
                                              'tree_root',
                                            ).filter(tree_root = 1)[0]

        name       = val['name'].replace('"', '')
        item_id    = val['id']
        parent_id  = val['parent_id']
        expand     = 'true' if val['expand_in_tree'] else 'false'
        javascript = 'tree.add("' + str(item_id) \
                                  + '", "' \
                                  + str(parent_id) \
                                  + '", "' \
                                  + name \
                                  + '", "", "", ' \
                                  + expand \
                                  + ', '

        javascript += 'false );\n' if item_id not in request.session['selected'][current_table] else 'true );\n'

        # now do follow-up query using root as parent
        javascript += create_tree_javascript(request, item_id, current_table)

    else:
        # for fossil, sex
        vals = current_model.objects.values('id', 'name').all()


    return render(request, 'primo/parameter_selection.jinja', {'current_table': current_table,
                                                               'vals': vals,
                                                               'javascript': javascript,
                                                              } )


@login_required
def query_setup(request, scalar_or_3d = 'scalar'):
    ''' For scalar queries send parameter_selection to frontend. Once all parameters are set, give option to call results, query_2d().

    Tables will be all of the tables that are available to search on for a particular search type (e.g. scalar or 3D).
        Of those tables sex and fossil will be pre-filled with all values selected. In that case,
        do a second query for all possible values and fill those values in. '''

    # if there's a POST, then parameter_selection has been called and some values have been sent back
    if request.method == 'POST':
        current_table = request.POST.get('table')

        if request.POST.get('commit') == 'Select Checked Options':
            # otherwise, either cancel select all was chosen
            selected_rows = []

            if request.POST.get('table') == 'taxon' or request.POST.get('table') == 'bodypart':
                # I have to look at all POST variables, and get the ones out that start with 'cb_main',
                # as those are set by nlstree.js.
                # All selected items cause one 'cb_main' variable to be set, as such: cb_main423 = 'on'.
                # So I need to get the number at the end, as that's the id of the selected item.
                for item in request.POST.items():
                    if item[0][:7] == 'cb_main':
                        selected_rows.append(int(item[0][7:]))

                if request.POST.get('table') == 'bodypart':
                    request.session['selected']['variable'] = []

            else: # Return is *not* from nlstree.js, so can just get id values.
                for item in request.POST.getlist('id'): # Because .get() returns only last item.
                                                        # Note that getlist() returns an empty list for any missing key.
                    selected_rows.append(int(item))
            request.session['selected'][current_table] = selected_rows

        elif request.POST.get('commit') == 'Select All':
            vals = apps.get_model( app_label  = 'primo',
                                   model_name = current_table.capitalize() \
                                 ).objects.values('id').all()
            request.session['selected'][current_table] = [val['id'] for val in vals]

    if not request.session['tables']: # if tables isn't set, query for all tables
                                      # and set up both tables and selected lists
        request.session['scalar_or_3d'] = scalar_or_3d

        # note for this query that "tables" is set as the related name in Models.py
        tables   = QueryWizardQuery.objects.get(data_table = scalar_or_3d.capitalize()).tables.all()
        selected = dict() # will hold all preselected data (e.g. sex: [1, 2, 3, 4, 5, 9])
        request.session['tables']   = []
        request.session['selected'] = dict()

        for table in tables:
            # if len(request.session['selected'][table.filter_table_name]) == 0:
            request.session['tables'].append( {'table_name': table.filter_table_name, 'display_name': table.display_name} )

            if table.preselected:
                model  = apps.get_model( app_label  = 'primo',
                                         model_name = table.filter_table_name.capitalize()
                                       )
                values = model.objects.values('id').all()
                # because vals is a list of dicts in format 'id': value
                request.session['selected'][table.filter_table_name] = [ value['id'] for value in values ]
            else:
                request.session['selected'][table.filter_table_name] = [] # so I can use 'if selected[table]' in query_setup.jinja

    tables   = request.session['tables']
    selected = request.session['selected']
    # I coudn't figure out any way to do this, other than to check each time
    finished = True

    for table in tables:
        if len(selected[table['table_name']]) == 0:
            finished = False

    request.session.modified = True
    return render( request, 'primo/query_setup.jinja', { 'scalar_or_3d': scalar_or_3d,
                                                         'tables':       tables,
                                                         'selected':     selected,
                                                         'finished':     finished,
                                                       }
                 )


def get_specimen_metadata():
    return [ ('specimen_id',        'Specimen ID'),
              ('hypocode',           'Hypocode'),
              ('collection_acronym', 'Collection Acronym'),
              ('catalog_number',     'Catalog No.'),
              ('taxon_name',         'Taxon name'),
              ('sex_type',           'Sex'),
              ('specimen_type',      'Type Status'),
              ('mass',               'Mass'),
              ('fossil_or_extant',   'Fossil or Extant'),
              ('captive_or_wild',    'Captive or Wild'),
              ('original_or_cast',   'Original or Cast'),
              ('session_comments',   'Session Comments'),
              ('specimen_comments',  'Specimen Comments'),
              ('age_class',          'Age Class'),
              ('locality_name',      'Locality'),
              ('country_name',       'Country'),
            ]

def query_2d(request, is_preview):
    """ Set up the 2D query SQL. Do query. Call result table display. """

    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Consider moving all of this, and 3D into db. As it was before, dammit.

    is_preview = True if is_preview == 'True' else False # convert from String
    if not request.user.is_authenticated or request.user.username == 'user':
        is_preview = True

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    base = 'SELECT `data_scalar`  . `id`             AS scalar_id, \
                   `specimen`     . `id`             AS specimen_id, \
                   `specimen`     . `hypocode`       AS hypocode, \
                   `institute`    . `abbr`           AS collection_acronym, \
                   `specimen`     . `catalog_number` AS catalog_number, \
                   `taxon`        . `name`           AS taxon_name, \
                   `specimen`     . `mass`           AS mass, \
                   `sex`          . `name`           AS sex_type, \
                   `specimen_type`. `name`           AS specimen_type, \
                   `fossil`       . `name`           AS fossil_or_extant, \
                   `captive`      . `name`           AS captive_or_wild, \
                   `original`     . `name`           AS original_or_cast, \
                   `variable`     . `label`          AS variable_label, \
                   `data_scalar`  . `value`          AS scalar_value, \
                   `age_class`    . `name`           AS age_class, \
                   `locality`     . `name`           AS locality_name, \
                   `country`      . `name`           AS country_name, \
                   `specimen`     . `comments`       AS specimen_comments, \
                   `session`      . `comments`       AS session_comments \
            FROM \
                  `variable` \
              INNER JOIN `data_scalar`    ON `data_scalar`   .`variable_id`       = `variable`      .`id` \
              INNER JOIN `session`        ON `data_scalar`   .`session_id`        = `session`       .`id` \
              INNER JOIN `specimen`       ON `session`       .`specimen_id`       = `specimen`      .`id` \
              INNER JOIN `original`       ON `session`       .`original_id`       = `original`      .`id` \
              INNER JOIN `taxon`          ON `specimen`      .`taxon_id`          = `taxon`         .`id` \
              INNER JOIN `sex`            ON `specimen`      .`sex_id`            = `sex`           .`id` \
              INNER JOIN `fossil`         ON `specimen`      .`fossil_id`         = `fossil`        .`id` \
              INNER JOIN `institute`      ON `specimen`      .`institute_id`      = `institute`     .`id` \
              INNER JOIN `captive`        ON `specimen`      .`captive_id`        = `captive`       .`id` \
              INNER JOIN `specimen_type`  ON `specimen`      .`specimen_type_id`  = `specimen_type` .`id` \
              INNER JOIN `age_class`      ON `specimen`      .`age_class_id`      = `age_class`     .`id` \
              INNER JOIN `locality`       ON `specimen`      .`locality_id`       = `locality`      .`id` \
              INNER JOIN `state_province` ON `locality`      .`state_province_id` = `state_province`.`id` \
              INNER JOIN `country`        ON `state_province`.`country_id`        = `country`       .`id`'

    where     = ' WHERE `sex`.`id` IN %s AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s AND `variable`.`id` IN %s '
    ordering  = ' ORDER BY `specimen`.`id`, `variable`.`label` ASC'
    final_sql = (base + where +  ordering + ';') # .format( concatVariableList(request.session['selected']['sex']) )

    # We have to query for the variable names separately.
    with connection.cursor() as variable_query:
        variable_query.execute( "SELECT `label` FROM `variable` WHERE `variable`.`id` IN %s ORDER BY `label` ASC;", [request.session['selected']['variable']] )
        variable_labels = [label for label in variable_query.fetchall()]

    # use cursor here?
    with connection.cursor() as cursor:
        cursor.execute( final_sql,
                        [ request.session['selected']['sex'],
                          request.session['selected']['fossil'],
                          request.session['selected']['taxon'],
                          # concatVariableList(request.session['selected']['bodypart']),
                          request.session['selected']['variable'],
                        ]
                      )
        # Now return all rows as a dictionary object. Note that each variable name will have its own row,
        # so I'm going to have to jump through some hoops to get the names out correctly for the
        # table headers in the view. TODO: There has to be a better way to do this.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        query_results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    are_results = True
    try:
        # if request.user.username == 'user':     # TODO: This could be a little more nicer.
        #     is_preview = True                   # It's already True if a preview was requested by the user.
        query_results = tabulate_2d(query_results, is_preview)
        request.session['query_results'] = query_results
    except:
        are_results = False

    # This is for use in exportCsvFile().
    request.session['variable_labels']   = variable_labels

    context = {
        'final_sql' : final_sql.replace('%s', '{}').format( request.session['selected']['sex'],
                                                            request.session['selected']['fossil'],
                                                            request.session['selected']['taxon'],
                                                            # concatVariableList(request.session['selected']['bodypart']),
                                                            request.session['selected']['variable'],
                                                          ),
        'query_results'     : query_results,
        'are_results'       : are_results,
        'total_specimens'   : len(query_results),
        'variable_labels'   : variable_labels,
        'variable_ids'      : request.session['selected']['variable'],
        'is_preview'        : is_preview,
        'specimen_metadata' : get_specimen_metadata(),
        'user'              : request.user.username,
    }

    return render(request, 'primo/query_results.jinja', context, )


@login_required
def query_start(request):
    """ Start query by creating necessary empty data structures. """
    request.session['tables']            = []
    request.session['selected']          = dict()
    request.session['selected']['table'] = []
    request.session['scalar_or_3d']      = ''
    return render(request, 'primo/query_start.jinja')


def query_3d(request, which_3d_output_type, is_preview):
    """ Set up the 3D query SQL. Do query for metadata. Call get_3D_data to get 3D points.
        Send results to either Morphologika or GRFND creator and downloader.
        If is_preview ignore which_output_type and show metadata preview for top five taxa. """

    is_preview = True if is_preview == 'True' else False # convert from String
    if not request.user.is_authenticated or request.user.username == 'user':
        is_preview = True

    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Move all of this and 3D into db. As it was before, dammit.


    # This is for cleaner code when composing header row for metadata csv.
    # First value is field name in DB, second is header name for metadata csv.


    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    # We'll only do metadata search first.

    # Note
    base = 'SELECT DISTINCT `specimen`     .`id`             AS specimen_id, \
                            `specimen`     .`hypocode`       AS hypocode, \
                            `institute`    .`abbr`           AS collection_acronym, \
                            `specimen`     .`catalog_number` AS catalog_number, \
                            `taxon`        .`name`           AS taxon_name, \
                            `specimen`     .`mass`           AS mass, \
                            `sex`          .`name`           AS sex_type, \
                            `specimen_type`.`name`           AS specimen_type, \
                            `fossil`       .`name`           AS fossil_or_extant, \
                            `captive`      .`name`           AS captive_or_wild, \
                            `original`     .`name`           AS original_or_cast, \
                            `protocol`     .`label`          AS protocol, \
                            `age_class`    .`name`           AS age_class, \
                            `locality`     .`name`           AS locality_name, \
                            `country`      .`name`           AS country_name, \
                            `session`      .`comments`       AS session_comments, \
                            `session`      .`id`             AS session_id, \
                            `specimen`     .`comments`       AS specimen_comments \
            FROM \
                `data_3d` \
            INNER JOIN `session`        ON `data_3d`       .`session_id`        = `session`       .`id` \
            INNER JOIN `specimen`       ON `session`       .`specimen_id`       = `specimen`      .`id` \
            INNER JOIN `taxon`          ON `specimen`      .`taxon_id`          = `taxon`         .`id` \
            INNER JOIN `sex`            ON `specimen`      .`sex_id`            = `sex`           .`id` \
            INNER JOIN `specimen_type`  ON `specimen`      .`specimen_type_id`  = `specimen_type` .`id` \
            INNER JOIN `fossil`         ON `specimen`      .`fossil_id`         = `fossil`        .`id` \
            INNER JOIN `institute`      ON `specimen`      .`institute_id`      = `institute`     .`id` \
            INNER JOIN `protocol`       ON `session`       .`protocol_id`       = `protocol`      .`id` \
            INNER JOIN `captive`        ON `specimen`      .`captive_id`        = `captive`       .`id` \
            INNER JOIN `original`       ON `session`       .`original_id`       = `original`      .`id` \
            INNER JOIN `age_class`      ON `specimen`      .`age_class_id`      = `age_class`     .`id` \
            INNER JOIN `locality`       ON `specimen`      .`locality_id`       = `locality`      .`id` \
            INNER JOIN `state_province` ON `locality`      .`state_province_id` = `state_province`.`id` \
            INNER JOIN `country`        ON `state_province`.`country_id`        = `country`       .`id`'

    where     = ' WHERE `sex`.`id` IN %s  AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s'
    # variables = ' AND `variable`.`id` IN (SELECT `id` FROM `datatype` WHERE `data_table` LIKE "data_3d")'
    ordering  = ' ORDER BY `specimen_id` ASC'
    limit = ''
    if is_preview:     # TODO: This could be a little more nicer.
        limit = ' LIMIT 5'
    final_sql = (base + where + ordering + limit + ';')

    # We skip varibles in 3D; we're getting all of them.

    # This is a list of all the session that will be returned from the query so I can send it to `get_3d()`
    # for a second query to get the actual data.
    sessions = set()

    with connection.cursor() as cursor:
        cursor.execute( final_sql,
                        [ request.session['selected']['sex'],
                          request.session['selected']['fossil'],
                          request.session['selected']['taxon'],
                        ],
                      )
        # Now return all rows as a dictionary object. Note that each variable name will have its own row,
        # so I'm going to have to jump through some hoops to get the names out correctly for the
        # table headers in the view. TODO: There has to be a better way to do that.

        # Note nice list comprehensions from the Django docs here:
        columns = [col[0] for col in cursor.description]
        query_results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        # Need to get session ids in case file will be downloaded. Single specimen per session is enforced at DB level.
        # This won't be used for preview.
        for item in query_results:
            sessions.add(item['session_id'])

    request.session['query']    = final_sql
    request.session['sessions'] = list(sessions)


    context = {
        'final_sql'     : final_sql.replace('%s', '{}').format( request.session['selected']['sex'],
                                                                request.session['selected']['fossil'],
                                                                request.session['selected']['taxon'],
                                                              ).replace('[', '(').replace(']',')'),
        'groups'            : request.user.get_group_permissions(),
        'is_preview'        : is_preview,
        'query_results'     : query_results,
        'specimen_metadata' : get_specimen_metadata(),
        'total_specimens'   : len(query_results),
        'user'              : request.user.username,
    }

    # if it's not a preview I need to get actual data and then send to morphologika or grfnd
    if not is_preview:
        request.session['total_specimens']   = context['total_specimens']

        get3D_data(request)
        return exportMorphologika(request)

    return render(request, 'primo/query_results.jinja', context )


def setUpDownload(request):
    """ Set the newline character, set name of file based on current time. Put both in session variable. """

    # Stupid Windows: we need to make sure the newline is set correctly. Abundance of caution.
    retStr = '\n'
    if request.META['HTTP_USER_AGENT'].lower().find( 'win' ):
        retStr = '\r\n'
    request.session['newlineChar'] = retStr

    # reminder: The format of the file name will be yy_mm_dd_hh_mm_ss_msmsms
    filename = datetime.now().strftime('%y_%m_%d_%H_%M_%S_%f') + '.csv'
    request.session['file_to_download'] = filename # this for use in download()


def tabulate_2d(query_results, is_preview):
    """ Return a list of dictionaries where each dictionary has the keys
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

        All requested variables """

    current_specimen = query_results[0]['hypocode']
    output = []
    current_dict = init_query_table(query_results[0])
    num_specimens = 1
    for row in query_results:
        # Is this a new specimen? If so need to set up new empty dictionary and
        # append it.
        if row['hypocode'] == current_specimen:
            current_dict[row['variable_label']] = row['scalar_value']
        else:
            num_specimens += 1
            output.append(current_dict)
            del(current_dict)
            current_dict = init_query_table(row)
            # This next so we can look up values quickly in view rather than having
            # to do constant conditionals.
            current_dict[row['variable_label']] = row['scalar_value']
            current_specimen = row['hypocode']
        # TODO: Figure out SQL so we don't have to do entire query and cull it here.
        if is_preview == True and num_specimens >= 15:
            break
    output.append(current_dict)
    return output

