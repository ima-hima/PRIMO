from django.conf import settings
from django.contrib import admin

# from django.contrib.auth import views as auth_views
from django.urls import include, path

from primo import views

admin.site.site_header = "PRIMO Adminstration"
# Next default: "Django site admin"
# admin.site.index_title = 'Features area'
# Next default: "Django site admin"
# admin.site.site_title = 'HTML title from adminsitration'

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls, name="admin"),
    path("email/", views.email, name="email"),
    path("entity_relation_diagram/", views.entity_relation_diagram, name="erd"),
    path("login/", views.log_in, name="login"),
    path("accounts/login/", views.log_in, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("download_success/", views.download_success, name="download_success"),
    path("export/<str:scalar_or_3d>/", views.export, name="export"),
    path(
        "export/<str:scalar_or_3d>/<str:which_3d_output_type>",
        views.export_3d,
        name="export",
    ),
    path(
        "parameter_selection/<str:current_table>",
        views.parameter_selection,
        name="parameter_selection",
    ),
    path("preview", views.preview, name="preview"),
    path(
        "initialize_query/<str:scalar_or_3d>",
        views.initialize_query,
        name="initialize_query",
    ),
    # If there's no GET, it defaults to scalar.
    path("initialize_query/", views.initialize_query, name="initialize_query"),
    path("query_start/", views.query_start, name="query_start"),
]

if settings.DEBUG:
    import debug_toolbar  # type: ignore

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
