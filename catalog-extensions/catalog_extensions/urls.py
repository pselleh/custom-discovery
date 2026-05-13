from django.urls import path
from catalog_extensions.api.views import UnifiedCatalogView

urlpatterns = [
    path("unified-catalog/", UnifiedCatalogView.as_view()),
]
