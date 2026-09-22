from django.urls import include, path

from catalog_extensions.api.views.courses import InternalCourseDetailView, InternalCourseListView
from catalog_extensions.api.views.programs import InternalProgramDetailView, InternalProgramListView

urlpatterns = [
    path("internal/courses/", InternalCourseListView.as_view(), name="internal-course-list"),
    path(
        "internal/courses/<path:course_key>/",
        InternalCourseDetailView.as_view(),
        name="internal-course-detail",
    ),
    path("internal/programs/", InternalProgramListView.as_view(), name="internal-program-list"),
    path(
        "internal/programs/<uuid:uuid>/",
        InternalProgramDetailView.as_view(),
        name="internal-program-detail",
    ),
    path("courses/", include("catalog_extensions.urls.courses")),
    path("programs/", include("catalog_extensions.urls.programs")),
    path("organizations/", include("catalog_extensions.urls.organizations")),
    path("subjects/", include("catalog_extensions.urls.subjects")),
    path("search/", include("catalog_extensions.urls.search")),
    path("media/", include("catalog_extensions.urls.media")),
    path("homepage/", include("catalog_extensions.urls.homepage")),
]
