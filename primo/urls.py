from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('email/', views.email,  name="email"),
    path('entity_relationship_diagram/', views.entity_relation_diagram, name="erd"),
    path('login/', views.log_in, name="login"),
    path('logout/', views.logout_view, name="logout"),

    path('download_success/',
        views.download_success,
        name="download_success"),

    path('export_scalar/',
    # path('exportCsvFile/(?P<current_table>\w+)/(?P<preview_only>\w+)',
        views.export_scalar,
        name="export_scalar"),

    path('parameter_selection/(<current_table>\w+)',
        views.parameter_selection,
        name="parameter_selection"),

    path('query_3d/(<which_3d_output_type>\w+)/(<preview_only>\w+)',
        views.query_3d,
        name="query_3d"),

    path('query_scalar/(<preview_only>\w+)',
        views.query_scalar,
        name="query_scalar"),

    path('query_setup/(<scalar_or_3d>\w+)',
        views.query_setup,
        name='query_setup'),

    path('query_setup/', views.query_setup, name="query_setup"),

    path('query_start/', views.query_start, name="query_start"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
