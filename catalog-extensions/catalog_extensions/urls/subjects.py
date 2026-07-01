from django.urls import path

from catalog_extensions.api.views.subjects import SubjectListView

urlpatterns = [
    path("", SubjectListView.as_view(), name="subject-list"),
]
