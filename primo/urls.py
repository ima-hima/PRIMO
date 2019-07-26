from django.conf         import settings
from django.conf.urls    import url
from django.urls         import include, path, re_path
from django.contrib      import admin
from django.contrib.auth import views                  as auth_views

from . import views

urlpatterns = [
    url(r'^$',                            views.IndexView.as_view(), name='index'),
    path('admin/',                        admin.site.urls,           name='admin'),
    url(r'^email/',                       views.email,               name="email"),
    url(r'^entity_relationship_diagram/', views.erd,                 name="erd"),
    url(r'login/',                        views.log_in,              name="login"),
    url(r'^logout/',                      views.logout_view,         name="logout"),

    url(r'^downloadSuccess/',
        views.downloadSuccess,
        name="downloadSuccess"),

    url(r'^export_2d/',
    # url(r'^exportCsvFile/(?P<current_table>\w+)/(?P<is_preview>\w+)',
        views.export_2d,
        name="export_2d"),

    url(r'^parameter_selection/(?P<current_table>\w+)',
        views.parameter_selection,
        name="parameter_selection"),

    url(r'^query_3d/(?P<which_3d_output_type>\w+)/(?P<is_preview>\w+)',
        views.query_3d,
        name="query_3d"),

    url(r'^query_2d/(?P<is_preview>\w+)',
        views.query_2d,
        name="query_2d"),

    url(r'^query_setup/(?P<scalar_or_3d>\w+)',
        views.query_setup,
        name='query_setup'),

    url(r'^query_setup/', views.query_setup, name="query_setup"),

    url(r'^query_start/', views.query_start, name="query_start"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
