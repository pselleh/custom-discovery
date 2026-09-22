from rest_framework.permissions import BasePermission


class HasRestrictedCatalogAccess(BasePermission):
    """Limit hidden catalog data to the Wagtail service account and administrators."""

    message = "Restricted catalog service permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.has_perm("catalog_extensions.view_restricted_catalog")
            )
        )
