from django.urls import path

from catalog_extensions.api.views.courses import CourseDetailView, CourseListView

urlpatterns = [
    path("", CourseListView.as_view(), name="course-list"),
    path("<path:course_key>/", CourseDetailView.as_view(), name="course-detail"),
]
