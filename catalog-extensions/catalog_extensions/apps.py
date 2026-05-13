from django.apps import AppConfig


class CatalogExtensionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog_extensions"

    def ready(self):
        from django.urls import include, path
        from django.urls import get_resolver

        resolver = get_resolver()

        resolver.url_patterns += [
            path(
                "api/catalog/",
                include("catalog_extensions.urls"),
            ),
        ]

