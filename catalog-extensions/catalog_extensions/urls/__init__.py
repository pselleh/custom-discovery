from django.urls import include, path

urlpatterns = [
    path("courses/", include("catalog_extensions.urls.courses")),
    path("programs/", include("catalog_extensions.urls.programs")),
    path("organizations/", include("catalog_extensions.urls.organizations")),
    path("subjects/", include("catalog_extensions.urls.subjects")),
    path("search/", include("catalog_extensions.urls.search")),
    path("media/", include("catalog_extensions.urls.media")),
    path("homepage/", include("catalog_extensions.urls.homepage")),
]
