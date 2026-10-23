from django.urls import path

from .views import (
    campaign_create,
    campaign_delete,
    campaign_duplicate,
    campaign_list,
    campaign_update,
    contact_error_report,
    contact_map,
    contact_upload,
    template_apply,
    template_delete,
    template_import,
    template_list,
    template_save,
)

app_name = "campaigns"

urlpatterns = [
    path("", campaign_list, name="list"),
    path("new/", campaign_create, name="create"),
    path("<uuid:pk>/edit/", campaign_update, name="update"),
    path("<uuid:pk>/delete/", campaign_delete, name="delete"),
    path("<uuid:pk>/duplicate/", campaign_duplicate, name="duplicate"),
    path("<uuid:pk>/contacts/", contact_upload, name="contacts"),
    path("<uuid:pk>/contacts/map/", contact_map, name="map"),
    path("<uuid:pk>/contacts/errors/", contact_error_report, name="error_report"),
    path("templates/", template_list, name="templates"),
    path("templates/save/", template_save, name="template_save"),
    path("templates/import/", template_import, name="template_import"),
    path("templates/<uuid:pk>/delete/", template_delete, name="template_delete"),
    path("templates/<uuid:pk>/apply/", template_apply, name="template_apply"),
]
