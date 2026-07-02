from django.urls import path

from catalog_extensions.api.views.programs import (
    ProgramDetailView,
    ProgramListView,
)

urlpatterns = [
    path("", ProgramListView.as_view(), name="program-list"),
    path("<uuid:uuid>/", ProgramDetailView.as_view(), name="program-detail"),
]
