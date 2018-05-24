from .forms                         import *
from .models                        import *
from csv                            import DictWriter
from datetime                       import datetime
from django.apps                    import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth            import authenticate, login, logout
from django.core.mail               import send_mail
from django.db                      import connection
from django.http                    import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts               import get_object_or_404, redirect, render, render_to_response
from django.urls                    import reverse
from django.utils                   import timezone
from django.views.generic           import TemplateView
from functools                      import reduce

import os


# Create your views here.

# def index(request):
#     return render(request, 'frontend/index.html')

class IndexView(TemplateView):
    """docstring for IndexView"""
    template_name = 'primo/index.jinja'


def concatVariableList(myList):
    return '(' + reduce((lambda b,c : b + str(c) + ','), myList, '' )[:-1] + ')'


def email(request):
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
    return render(request, 'primo/erd.jinja')


def exportCsvFile(fieldNames, values):
    ''' This is for 2D data. For 3D data we write either or Morphologika or GRFND file. '''
    #reminder: The format will be yy_mm_dd_hh_mm
    with open(datetime.now().strftime('%y_%m_%d_%H_%M'), 'w') as csvfile:
        csv_rows = [
            dict(zip(fieldNames, values))
        ]

        writer = DictWriter(csvfile, fieldnames=fieldNames)

        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)


def exportMorphologika(fieldNames, metaData, values):
    retStr = '\n'
    if find( HttpRequestAgent.HTTP_USER_AGENT.lower(), 'win' ):
        retStr = '\r\n'

    missing_pts = {}

    metaDataLen = len(metaData)

    dataOutString = "[individuals]retStrretStr"
    dataOutString += metaDataLen + "retStrretStr"
    dataOutString += "[landmarks]retStrretStr"
    dataOutString += len(values) / metaDataLen + "retStrretStr"
    dataOutString += "[dimensions]retStrretStr" + "3retStrretStr"
    dataOutString += "[names]retStrretStr"
    for key, value in metaData:
        dataOutString += value['specimen_id'] + "retStr"

    dataOutString += "retStr" + "[rawpoints]retStr"
    flag = ''
    for key, value in values:
        if value['specimen_id'] != flag:
            flag = value['specimen_id']
            dataOutString += "retStr'" + preg_replace('/ /', '_', value['hypocode']) + "retStr"
            point_ctr = 1;
        if value['x'] == '9999.0000' and value['y'] == '9999.0000' and value['z'] == '9999.0000':
            dataOutString += '9999\t9999\t9999' + retStr
            if value['specimen_id'] not in missing_pts:
                missing_pts[ value['specimen_id'] ] = point_ctr;
            else:
                missing_pts[ value['specimen_id'] ] += ' ' + point_ctr;

        else:
            dataOutString += value['x'] + "\t" + value['y'] + "\t" + value['z'] + "retStr";

        point_ctr++;

#         } else if ($which == 'grfnd') {
#             dataOutString = '1 ' + count($metaData) + 'L ' +  3 * (count(values) / count($metaData)). " 1 9999 DIM=3retStr";
#             foreach ($metaData as $key => $value) {
#                 dataOutString += $metaData[$key]['specimen_id'] + "retStr";
#             }
#             $flag = '';
#             foreach (values as $key => $value) {
#                 if ( (value['specimen_id'] != $flag) ) {
#                     $flag = value['specimen_id'];
#                     dataOutString += "retStr";
#                     point_ctr = 1;
#                 }
#                 if (value['x'] == '9999.0000' and value['y'] == '9999.0000' and value['z'] == '9999.0000') {
#                     dataOutString += "9999\t9999\t9999retStr";
#                     if( !isset(missing_pts[value['specimen_id'] ]) ) {
#                         missing_pts[ value['specimen_id'] ] = point_ctr;
#                     } else {
#                         missing_pts[ value['specimen_id'] ] += ' ' + point_ctr;
#                     }
#                 } else {
#                     dataOutString += value['x'] + "\t" + value['y'] + "\t" + value['z'] + "retStr";
#                 }
#                 point_ctr++;
#             }
#         }

#         $folderName = 'PRIMO_3D_' + uniqid();
#         $metaOutString = '';
#         if (mkdir ("/tmp/$folderName")) {
#             $fp = fopen("/tmp/$folderName/specimen_data.csv", 'w');
#             fwrite($fp, "specimen id, hypocode, institute, catalog number, taxon name, sex, fossil or extant, captive or wild-caught, original or cast, protocol, session comments, specimen comments, missing points (indexed by specimen starting at 1)retStr");
#             fwrite ($fp, implode(', ', $fieldNamesArray));
#             foreach ($metaData as $key => $value) {
#                 foreach ($metaData[$key] as $metaKey => $metaVal) {
#                     if( $metaKey !== 'datindex' and $metaKey !== 'variable_id' ) {
#                         $metaOutString += $this->fixQuotes($metaVal) + ',';
#                     }
#                 }
#                 if( isset(missing_pts[ $metaData[$key]['specimen_id'] ]) ) {
#                     $metaOutString += missing_pts[ $metaData[$key]['specimen_id'] ];
#                 }
#                 $metaOutString += "retStr";
#             }
#             fwrite($fp, $metaOutString);
#             //fwrite($fp, missing_pts);
#             fclose($fp);

#             $fp = fopen("/tmp/$folderName/3d_data.txt", 'w');
#             fwrite($fp, dataOutString);
#             fclose($fp);
#             exec("tar -czf /tmp/$folderName.tar.gz /tmp/$folderName/");
#             unlink("/tmp/$folderName/3d_data.txt");
#             unlink("/tmp/$folderName/specimen_data.csv");
#             rmdir("/tmp/$folderName");

#             $file = file_get_contents ("/tmp/$folderName.tar.gz");
#             header("Content-type: application/x-compressed");
#             header('Content-disposition: gz; filename=PRIMO_3D_output_' + date("Y-m-d-H-i-s") + "_$which.tar.gz; size=".strlen($file));
#             echo $file;

#             unlink("/tmp/$folderName.tar.gz");
#         }


#         exit;
#     }


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
def query_setup(request, scalar_or_3d = 'scalar'):
    '''tables will be all of the tables that are available to search on for a particular search type (e.g. scalar or 3D).
       Some of those tables, like sex, should be pre-filled with all values selected. In that case,
       do a second query for all possible values and fill those values in.'''
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
        tables   = QueryWizardQuery.objects.get(query_type=scalar_or_3d.capitalize()).tables.all()
        selected = dict() # will hold all preselected data (e.g. sex: [1, 2, 3, 4, 5, 9])
        request.session['tables']   = []
        request.session['selected'] = dict()
        for table in tables:
            #if len(request.session['selected'][table.filter_table_name]) == 0:
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
                                                        'tables':   tables,
                                                        'selected': selected,
                                                        'finished': finished,
                                                       }
                 )


@login_required
def query_start(request):
    request.session['tables']            = []
    request.session['selected']          = dict()
    request.session['selected']['table'] = []
    request.session['scalar_or_3d']      = ''
    return render(request, 'primo/query_start.jinja')


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


def create_tree_javascript(request, parent_id, current_table):
    ''' Creates javascript for heirarchical tree display. Formal parameters for tree.add() are:
        add(node_id, parent_id, node name, url, icon, expand?, precheck?, extra info, text on mouse hover).
        The last two are currently unneeded, and therefore ignored below.
        Function is recursive on parent_id and returns a properly-formatted string of Javascript code,
        although from reading nlstree docs (https://www.addobject.com/nlstree), it seems order is unimportant,
        so recursion may be unnecessary (wasteful?). Oh, wait: necessary because of if statement dealing with Eocatarrhini.
        Okay, so *eventually* unnecessary?'''
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


def query_2d(request, is_preview):
    # TODO: Look into doing this all with built-ins, rather than with .raw()

    base = 'SELECT `scalar`.`id`, \
                   `specimen` .`id`             AS specimen_id, \
                   `specimen` .`hypocode`       AS hypocode, \
                   `institute`.`institute_abbr` AS collection_acronym, \
                   `specimen` .`catalog_number` AS catalog_number, \
                   `specimen` .`mass`           AS mass, \
                   `taxon`    .`name`           AS taxon_name, \
                   `sex`      .`name`           AS sex_type, \
                   `fossil`   .`name`           AS fossil_or_extant, \
                   `captive`  .`name`           AS captive_or_wild, \
                   `original` .`name`           AS original_or_cast, \
                   `variable` .`label`          AS variable_label,\
                   `scalar`   .`value`          AS scalar_value,\
                   `session`  .`comments`       AS session_comments, \
                   `specimen` .`comments`       AS specimen_comments \
            FROM `scalar` \
\
            Inner Join `variable`          ON `scalar`           .`variable_id`  = `variable` .`id` \
            Inner Join `session`           ON `scalar`           .`session_id`   = `session`  .`id` \
            Inner Join `specimen`          ON `session`          .`specimen_id`  = `specimen` .`id` \
            Inner Join `taxon`             ON `specimen`         .`taxon_id`     = `taxon`    .`id` \
            Inner Join `sex`               ON `specimen`         .`sex_id`       = `sex`      .`id` \
            Inner Join `fossil`            ON `specimen`         .`fossil_id`    = `fossil`   .`id` \
            Inner Join `institute`         ON `specimen`         .`institute_id` = `institute`.`id` \
            Inner Join `captive`           ON `specimen`         .`captive_id`   = `captive`  .`id` \
            Inner Join `original`          ON `session`          .`original_id`  = `original` .`id`'

    where     = ' WHERE `sex`.`id` IN %s  AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s AND `variable`.`id` IN %s '
    ordering  = ' ORDER BY `specimen`.`id`, `variable`.`label` ASC'
    limit     = ' LIMIT 15' if is_preview else ''
    final_sql = (base + where +  ordering + limit + ';') # .format( concatVariableList(request.session['selected']['sex']) )
    request.session['query'] = final_sql

    with connection.cursor() as variable_query:
        variable_query.execute( "SELECT `label` FROM `variable` WHERE `variable`.`id` IN %s;", [request.session['selected']['variable']] )
        variable_labels = [label for label in variable_query.fetchall()]

    # use cursor here?
    with connection.cursor() as cursor:
        a = 5
        cursor.execute( final_sql, [
                           request.session['selected']['sex'],
                           request.session['selected']['fossil'],
                           request.session['selected']['taxon'],
                           # # concatVariableList(request.session['selected']['bodypart']),
                           request.session['selected']['variable'],
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

    context = {
        'final_sql' : final_sql.replace('%s', '{}').format( request.session['selected']['sex'],
                                                            request.session['selected']['fossil'],
                                                            request.session['selected']['taxon'],
                                                            # concatVariableList(request.session['selected']['bodypart']),
                                                            request.session['selected']['variable'],
                                                          ),
        'query_results'   : query_results,
        'variable_labels' : variable_labels,
        'variable_ids'    : request.session['selected']['variable'],
    }

    return render(request, 'primo/query_results.jinja', context, )


def query_3d(request, which_3d_output_type, is_preview):
    # TODO: Look into doing this all with built-ins, rather than with .raw()

    base = 'SELECT DISTINCT `data3d`   .`id`, \
                            `specimen` .`id`             AS specimen_id, \
                            `specimen` .`hypocode`       AS hypocode, \
                            `institute`.`institute_abbr` AS collection_acronym, \
                            `specimen` .`catalog_number` AS catalog_number, \
                            `specimen` .`mass`           AS mass, \
                            `taxon`    .`name`           AS taxon_name, \
                            `sex`      .`name`           AS sex_type, \
                            `fossil`   .`name`           AS fossil_or_extant, \
                            `captive`  .`name`           AS captive_or_wild, \
                            `original` .`name`           AS original_or_cast, \
                            `protocol` .`label`          AS protocol, \
                            `session`  .`comments`       AS session_comments, \
                            `specimen` .`comments`       AS specimen_comments, \
                            `data3d`   .`x`, \
                            `data3d`   .`y`, \
                            `data3d`   .`z`, \
                            `data3d`   .`datindex`, \
                            `data3d`   .`variable_id` \
            FROM data3d \
\
            Inner Join `variable`          ON `data3d`           .`variable_id`  = `variable`  .`id` \
            Inner Join `bodypart_variable` ON `bodypart_variable`.`variable_id`  = `variable`  .`id` \
            Inner Join `bodypart`          ON `bodypart_variable`.`bodypart_id`  = `bodypart`  .`id` \
            Inner Join `session`           ON `data3d`           .`session_id`   = `session`   .`id` \
            Inner Join `specimen`          ON `session`          .`specimen_id`  = `specimen`  .`id` \
            Inner Join `taxon`             ON `specimen`         .`taxon_id`     = `taxon`     .`id` \
            Inner Join `sex`               ON `specimen`         .`sex_id`       = `sex`       .`id` \
            Inner Join `fossil`            ON `specimen`         .`fossil_id`    = `fossil`    .`id` \
            Inner Join `institute`         ON `specimen`         .`institute_id` = `institute` .`id` \
            Inner Join `protocol`          ON `session`          .`protocol_id`  = `protocol`  .`id` \
            Inner Join `captive`           ON `specimen`         .`captive_id`   = `captive`   .`id` \
            Inner Join `original`          ON `session`          .`original_id`  = `original`  .`id`'

    where     = ' WHERE `sex`.`id` IN %s  AND `fossil`.`id` IN %s AND `taxon`.`id` IN %s'
    ordering  = ' ORDER BY `specimen`.`id`, `variable`.`id`, `data3d`.`datindex` ASC'
    limit     = ' LIMIT 15' if is_preview else ''
    final_sql = (base + where +  ordering + limit + ';') # .format( concatVariableList(request.session['selected']['sex']) )
    request.session['query'] = final_sql

    with connection.cursor() as variable_query:
        variable_query.execute( "SELECT `label` FROM `variable` WHERE `variable`.`id` IN %s;", [request.session['selected']['variable']] )
        variable_labels = [label for label in variable_query.fetchall()]

    with connection.cursor() as cursor:

        cursor.execute( final_sql, [
                           concatVariableList(request.session['selected']['sex']),
                           concatVariableList(request.session['selected']['fossil']),
                           concatVariableList(request.session['selected']['taxon']),
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

    context = {
        'final_sql' : final_sql.replace('%s', '{}').format( request.session['selected']['sex'],
                                                            request.session['selected']['fossil'],
                                                            request.session['selected']['taxon'],
                                                            # concatVariableList(request.session['selected']['bodypart']),
                                                            request.session['selected']['variable'],
                                                          ),
        'query_results'   : query_results,
        'variable_labels' : variable_labels,
        'variable_ids'    : request.session['selected']['variable'],
    }

    return render(request, 'primo/query_results.jinja', context, )
