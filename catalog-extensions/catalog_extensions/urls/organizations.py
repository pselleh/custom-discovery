from django.urls import path

from catalog_extensions.api.views.organizations import OrganizationListView

urlpatterns = [
    path("", OrganizationListView.as_view(), name="organization-list"),
]
