"""URL configuration for hub."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="confronto:risultati", permanent=False)),
    path("confronto/", include("confronto.urls")),
]

# Django admin is a local-development tool. Azure users authenticate with Entra.
if not settings.AZURE_ENTRA_AUTH:
    urlpatterns.insert(0, path("admin/", admin.site.urls))
