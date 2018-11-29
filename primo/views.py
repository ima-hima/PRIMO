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
        Oh, wait: necessary because of if statement dealing with Eocatarrhini.
        Okay, so *eventually* unnecessary? """
    javascript = ''
    js_item_delimiter = '", "'

    vals = apps.get_model(app_label='primo',
                          model_name=current_table.capitalize()).objects.values('id',
                                                                                'name',
                                                                                'parent_id',
                                                                                'expand_in_tree',
                                                                               ).filter(parent_id=parent_id)
    #print(vals)
    for val in vals:
        # remove quote marks from `name`, as they'll screw up Javascript
        name      = val['name'].replace('"', '')
        item_id   = val['id']
        parent_id = val['parent_id']
        expand    = 'true' if val['expand_in_tree'] else 'false'
        #print(name)
        if name != 'Eocatarrhini': # I'm not clear why I don't need to recurse up Eocatarrhini heirarchy
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
    remove( path.join(settings.DOWNLOAD_ROOT, request.session['file_to_download']) )
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


def exportCsvFile(request):
    """ Collate data returned from SQL query, render into csv, save csv to tmp directory,
        start download.
        This is for 2D data. For 3D data we write either or Morphologika or GRFND file. """

    setUpDownload(request)

    with open( path.join(settings.DOWNLOAD_ROOT, request.session['file_to_download']), newline=request.session['newlineChar'] ) as f:
        csvfile = File(f)
        meta_names = [ m[0] for m in request.session['specimen_metadata'] ]
        var_names  = [ v[0] for v in request.session['variable_labels'] ]
        #     (request.session['specimen_metadata'], request.session['query_results']))
        # ]

        writer = DictWriter(csvfile, fieldnames=meta_names + var_names)

        writer.writeheader()
        for row in request.session['query_results']:
            inDict = { k : row[k] for k in row.keys() if k != 'scalar_value' and k != 'variable_label' }
            writer.writerow(inDict)
    return download(request)


def exportMorphologika(request, fieldNames, metaData, values):
    """ Collate data returned from 3D SQL query.
        Print out two files: a csv of metadata and a Morphologika file. Fields included in metadata
        are enumerated below. """

    setUpDownload(request)

    retStr = '\n'
    # TODO: deal with this
    # if( strpos( strtolower( $_SERVER['HTTP_USER_AGENT'] ), 'win' ) ) {
    #         $ret = "\r\n";
    # }

    missing_pts = {} # These will be output in metadata csv file.

    metaDataLen = len(metaData)

    dataOutString =  '[individuals]' + retStr * 2
    for strVal in [metaDataLen, '[landmarks]', len(values) / metaDataLen, '[dimensions]', '3', '[names]']:
        dataOutString += strVal + retStr * 2

    for key, value in metaData:
        dataOutString += value['specimen_id'] + retStr

    dataOutString += retStr + '[rawpoints]' + retStr
    flag = ''   # what is this for?
    for key, value in values:
        if value['specimen_id'] != flag:
            flag = value['specimen_id']
            dataOutString += retStr + "'" + preg_replace('/ /', '_', value['hypocode']) + retStr
            point_ctr = 1;
        if value['x'] == '9999.0000' and value['y'] == '9999.0000' and value['z'] == '9999.0000':
            dataOutString += '9999\t9999\t9999' + retStr
            if value['specimen_id'] not in missing_pts:
                missing_pts[ value['specimen_id'] ] = point_ctr;
            else:
                missing_pts[ value['specimen_id'] ] += ' ' + point_ctr;

        else:
            dataOutString += value['x'] + "\t" + value['y'] + "\t" + value['z'] + retStr

        point_ctr += 1

        dirName = 'PRIMO_3D_' + uuid1()  # uuid1() creates UUID string
        metaOutString = '';
        with open( path.join(settings.DOWNLOAD_ROOT, request.session['file_to_download']), newline=request.session['newlineChar'] ) as f:
            csvfile = File(f)

            outFile.write( ' specimen id, hypocode, institute, catalog number, taxon name, mass, sex, fossil or extant, captive or wild-caught, original or cast, protocol, session comments, specimen comments, missing points (indexed by specimen starting at 1)' + retStr )
            outFile.write( ', '.join(fieldNamesArray) )
            for key, value in metaData:
                for metaKey, metaValue in value: ## was    metaData[key]:
                    if metaKey != 'datindex' and metaKey != 'variable_id':
                        metaOutString += fixQuotes(metaVal) + ','
                try:
                    metaOutString += missing_pts[ value['specimen_id'] ]
                except:
                    pass

                metaOutString += retStr;

            outFile.write(metaOutString)
            outFile.close()

            outFile = open('/tmp/' + dirName + '/3d_data.txt', 'w');
            outFile.write(dataOutString)
            outFile.close()
            exec("tar -czf /tmp/$folderName.tar.gz /tmp/$folderName/");
            unlink("/tmp/$folderName/3d_data.txt");
            unlink("/tmp/$folderName/specimen_data.csv");
            rmdir("/tmp/$folderName");

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
    #  Quotes in the value must be quoted.
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
    #  Quotes equal sign (Excel interprets this as a formula).
    # -----------------------------------------------------------------
    elif inStr.find('=') >= 0:
        needQuote = True

    if (needQuote):
        inStr = '"' + inStr + '"'

    return inStr


def init_query_table(query_result):
    """ Initialize query table (actually a dictionary) that is to be used for data
        that will be pushed out to view. A single query row is received and put into
        dictionary. """
    output = {'specimen_id'        : query_result['specimen_id'],
              'hypocode'           : query_result['hypocode'],
              'collection_acronym' : query_result['collection_acronym'],
              'catalog_number'     : query_result['catalog_number'],
              'mass'               : query_result['mass'],
              'taxon_name'         : query_result['taxon_name'],
              'sex_type'           : query_result['sex_type'],
              'fossil_or_extant'   : query_result['fossil_or_extant'],
              'captive_or_wild'    : query_result['captive_or_wild'],
              'original_or_cast'   : query_result['original_or_cast'],
              'variable_label'     : query_result['variable_label'],
              'scalar_value'       : query_result['scalar_value'],
              'session_comments'   : query_result['session_comments'],
              'specimen_comments'  : query_result['specimen_comments'],
             }
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

    current_model = apps.get_model( app_label = 'primo', model_name = current_table.capitalize() )

    if current_table == 'variable':
        if len(request.session.get('selected')['bodypart']) > 0:
            bodypart_list          = request.session.get('selected')['bodypart']
            bodypart_variable_ids  = current_model.objects.values('id').filter(bodypartvariable__bodypart_id__in=bodypart_list)
            variable_ids           = BodypartVariable.objects.values('variable_id').filter(pk__in=bodypart_variable_ids)
            vals                   = current_model.objects.values('id',
                                                                  'name',
                                                                  'label',
                                                                 ).filter(pk__in=variable_ids).order_by('id')
        else:
            vals = apps.get_model( app_label='primo',
                                   model_name=current_table.capitalize() \
                                 ).objects.values('name',
                                                  'label',
                                                  'bodypartvariable__bodypart_id',
                                                 ).all()

    elif current_table == 'bodypart' or current_table == 'taxon':
        vals = []
        # do original query to get root of tree
        val = apps.get_model( app_label='primo',
                              model_name=current_table.capitalize()
                            ).objects.values('id', 'name', 'parent_id', 'expand_in_tree').filter(tree_root = 1)[0]

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
    """ Tables will be all of the tables that are available to search on for a particular search type (e.g. scalar or 3D).
        Some of those tables, like sex, should be pre-filled with all values selected. In that case,
        do a second query for all possible values and fill those values in. """
    # if there's a POST, then parameter_selection has been called, and some values have been sent back
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

    if not request.session.get('tables'): # if tables isn't set, query for all tables,
                                          # and set up both tables and selected lists
        request.session['scalar_or_3d'] = scalar_or_3d

        # note for this query that "tables" is set as the related name in Models.py
        tables   = QueryWizardQuery.objects.get(data_table=scalar_or_3d.capitalize()).tables.all()
        selected = dict() # will hold all preselected data (e.g. sex: [1, 2, 3, 4, 5, 9])
        request.session['tables']   = []
        request.session['selected'] = dict()
        for table in tables:
            # if len(request.session['selected'][table.filter_table_name]) == 0:
            request.session['tables'].append( {'table_name': table.filter_table_name, 'display_name': table.display_name} )
            if table.preselected:
                model  = apps.get_model(app_label='primo', model_name=table.filter_table_name.capitalize())
                values = model.objects.values('id').all()
                # because vals is a list of dicts in format 'id': value
                request.session['selected'][table.filter_table_name] = [ value['id'] for value in values ]
            else:
                request.session['selected'][table.filter_table_name] = [] # so I can use 'if selected[table]' in query_setup.jinja
    tables   = request.session.get('tables')
    selected = request.session.get('selected')
    # I coudn't figure out any other way to do this, other than to check each time
    finished = True
    for table in tables:
        if len(selected[table['table_name']]) == 0:
            finished = False
    request.session.modified = True
    return render( request, 'primo/query_setup.jinja', {'scalar_or_3d': scalar_or_3d,
                                                        'tables':       tables,
                                                        'selected':     selected,
                                                        'finished':     finished,
                                                       }
                 )


def query_2d(request, is_preview):
    """ Set up the 2D query SQL. Do query. Call result table display. """
    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Move all of this, and 3D into db. As it was before, dammit.

    # This is for cleaner code when composing header row for csv.
    specimen_metadata = [ ('specimen_id',        'Specimen ID'),
                          ('hypocode',           'Hypocode'),
                          ('collection_acronym', 'Collection Acronym'),
                          ('catalog_number',     'Catalog No.'),
                          ('taxon_name',         'Taxon name'),
                          ('sex_type',           'Sex'),
                          ('mass',               'Mass'),
                          ('fossil_or_extant',   'Fossil or Extant'),
                          ('captive_or_wild',    'Captive or Wild'),
                          ('original_or_cast',   'Original or Cast'),
                          ('session_comments',   'Session Comments'),
                          ('specimen_comments',  'Specimen Comments'),
                        ]

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    base = 'SELECT `data_scalar`. `id`             AS  scalar_id, \
                   `specimen`   . `id`             AS  specimen_id, \
                   `specimen`   . `hypocode`       AS  hypocode, \
                   `institute`  . `abbr`           AS  collection_acronym, \
                   `specimen`   . `catalog_number` AS  catalog_number, \
                   `taxon`      . `name`           AS  taxon_name, \
                   `specimen`   . `mass`           AS  mass, \
                   `sex`        . `name`           AS  sex_type, \
                   `fossil`     . `name`           AS  fossil_or_extant, \
                   `captive`    . `name`           AS  captive_or_wild, \
                   `original`   . `name`           AS  original_or_cast, \
                   `variable`   . `label`          AS  variable_label, \
                   `data_scalar`. `value`          AS  scalar_value, \
                   `session`    . `comments`       AS  session_comments, \
                   `specimen`   . `comments`       AS  specimen_comments '

    base += 'FROM `data_scalar` \
             INNER JOIN `variable` ON `data_scalar`.`variable_id`  = `variable` .`id` \
             INNER JOIN `session`  ON `data_scalar`.`session_id`   = `session`  .`id` \
             INNER JOIN `specimen` ON `session`    .`specimen_id`  = `specimen` .`id` \
             INNER JOIN `taxon`    ON `specimen`   .`taxon_id`     = `taxon`    .`id` \
             INNER JOIN `sex`      ON `specimen`   .`sex_id`       = `sex`      .`id` \
             INNER JOIN `fossil`   ON `specimen`   .`fossil_id`    = `fossil`   .`id` \
             INNER JOIN `institute`ON `specimen`   .`institute_id` = `institute`.`id` \
             INNER JOIN `captive`  ON `specimen`   .`captive_id`   = `captive`  .`id` \
             INNER JOIN `original` ON `session`    .`original_id`  = `original` .`id`'

    where     = ' WHERE `sex`.`id` IN %s  AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s AND `variable`.`id` IN %s '
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
        if request.user.username == 'user':     # TODO: This could be a little more nicer.
            is_preview = True                   # It's already True if a preview was requested by the user.
        query_results = tabulate_2d(query_results, is_preview)
        request.session['query_results'] = query_results
    except:
        are_results = False

    # These are for use in exportCsvFile().
    request.session['specimen_metadata'] = specimen_metadata
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
        'total'             : len(query_results),
        'variable_labels'   : variable_labels,
        'variable_ids'      : request.session['selected']['variable'],
        'is_preview'        : is_preview,
        'specimen_metadata' : specimen_metadata
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
    """ Set up the 3D query SQL. Do query. Send results to either Morphologika or
        GRFND creator and downloader. If is_preview ignore which_output_type. """
    # TODO: Look into doing this all with built-ins, rather than with .raw()
    # TODO: Move all of this, and 3D into db. As it was before, dammit.

    # This is for cleaner code when composing header row for metadata csv.
    specimen_metadata = [ ('specimen_id',        'Specimen ID'),
                          ('hypocode',           'Hypocode'),
                          ('collection_acronym', 'Collection Acronym'),
                          ('catalog_number',     'Catalog No.'),
                          ('taxon_name',         'Taxon name'),
                          ('sex_type',           'Sex'),
                          ('mass',               'Mass'),
                          ('fossil_or_extant',   'Fossil or Extant'),
                          ('captive_or_wild',    'Captive or Wild'),
                          ('original_or_cast',   'Original or Cast'),
                          ('protocol',           'Protocol'),
                          ('session_comments',   'Session Comments'),
                          ('specimen_comments',  'Specimen Comments'),
                          ('x',                  'x'),
                          ('y',                  'y'),
                          ('z',                  'z'),
                          ('datindex',           'Data index'),
                          ('variable_id',        'Variable ID'),
                        ]

    # This is okay to include in publicly-available code (i.e. git), because
    # the database structure diagram is already published on the website anyway.
    base = 'SELECT DISTINCT `specimen` .`id`             AS specimen_id, \
                            `specimen` .`hypocode`       AS hypocode, \
                            `institute`.`abbr`           AS collection_acronym, \
                            `specimen` .`catalog_number` AS catalog_number, \
                            `taxon`    .`name`           AS taxon_name, \
                            `specimen` .`mass`           AS mass, \
                            `sex`      .`name`           AS sex_type, \
                            `fossil`   .`name`           AS fossil_or_extant, \
                            `captive`  .`name`           AS captive_or_wild, \
                            `original` .`name`           AS original_or_cast, \
                            `protocol` .`label`          AS protocol, \
                            `session`  .`comments`       AS session_comments, \
                            `specimen` .`comments`       AS specimen_comments, \
                            `data_3d`  .`x`, \
                            `data_3d`  .`y`, \
                            `data_3d`  .`z`, \
                            `data_3d`  .`datindex`, \
                            `data_3d`  .`variable_id` \
            FROM \
                data_3d \
            INNER JOIN `variable`          ON `data_3d`          .`variable_id`  = `variable`  .`id` \
            INNER JOIN `bodypart_variable` ON `bodypart_variable`.`variable_id`  = `variable`  .`id` \
            INNER JOIN `bodypart`          ON `bodypart_variable`.`bodypart_id`  = `bodypart`  .`id` \
            INNER JOIN `session`           ON `data_3d`          .`session_id`   = `session`   .`id` \
            INNER JOIN `specimen`          ON `session`          .`specimen_id`  = `specimen`  .`id` \
            INNER JOIN `taxon`             ON `specimen`         .`taxon_id`     = `taxon`     .`id` \
            INNER JOIN `sex`               ON `specimen`         .`sex_id`       = `sex`       .`id` \
            INNER JOIN `fossil`            ON `specimen`         .`fossil_id`    = `fossil`    .`id` \
            INNER JOIN `institute`         ON `specimen`         .`institute_id` = `institute` .`id` \
            INNER JOIN `protocol`          ON `session`          .`protocol_id`  = `protocol`  .`id` \
            INNER JOIN `captive`           ON `specimen`         .`captive_id`   = `captive`   .`id` \
            INNER JOIN `original`          ON `session`          .`original_id`  = `original`  .`id`'

    where     = ' WHERE `sex`.`id` IN %s  AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s'
    # variables = ' AND `variable`.`id` IN (SELECT `id` FROM `datatype` WHERE `data_table` LIKE "data_3d")'
    ordering  = ' ORDER BY `specimen`.`id`, `variable_id`, `data_3d`.`datindex` ASC'
    final_sql = (base + where + ordering + ';')

    # We skip varibles in 3D; we're getting all of them.

    with connection.cursor() as cursor:
        cursor.execute( final_sql, [
                           request.session['selected']['sex'],
                           request.session['selected']['fossil'],
                           request.session['selected']['taxon'],
                        ]
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

    are_results = bool(query_results)

    # try:
    #     if request.user.username == 'user':     # TODO: This could be a little more nicer.
    #         is_preview = True                   # It's already True if a preview was requested by the user.
    #     query_results = tabulate_2d(query_results, is_preview)
    #     request.session['query_results'] = query_results
    # except:
    #     are_results = False

    request.session['query'] = final_sql

    context = {
        'final_sql'     : final_sql.replace('%s', '{}').format( request.session['selected']['sex'],
                                                                request.session['selected']['fossil'],
                                                                request.session['selected']['taxon'],
                                                              ).replace('[', '(').replace(']',')'),
        'query_results'     : query_results,
        'groups'            : request.user.get_group_permissions(),
        'specimen_metadata' : specimen_metadata,
    }

    return render(request, 'primo/query_results.jinja', context, )


def setUpDownload(request):
    """ Set the newline character, set name of file based on current time. Put both in session variable. """

    # Stupid Windows: we need to make sure the newline is set correctly. Abundance of caution.
    retStr = '\n'
    if find( HttpRequestAgent.HTTP_USER_AGENT.lower(), 'win' ):
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

