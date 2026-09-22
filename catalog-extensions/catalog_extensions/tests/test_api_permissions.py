from types import SimpleNamespace
from unittest import TestCase

from catalog_extensions.api.permissions import HasRestrictedCatalogAccess


class RestrictedCatalogPermissionTests(TestCase):
    def _request(self, authenticated, superuser=False, permitted=False):
        user = SimpleNamespace(
            is_authenticated=authenticated,
            is_superuser=superuser,
            has_perm=lambda permission: permitted,
        )
        return SimpleNamespace(user=user)

    def test_anonymous_user_is_denied(self):
        self.assertFalse(HasRestrictedCatalogAccess().has_permission(self._request(False), None))

    def test_ordinary_authenticated_user_is_denied(self):
        self.assertFalse(HasRestrictedCatalogAccess().has_permission(self._request(True), None))

    def test_service_permission_is_accepted(self):
        self.assertTrue(HasRestrictedCatalogAccess().has_permission(self._request(True, permitted=True), None))

    def test_superuser_is_accepted(self):
        self.assertTrue(HasRestrictedCatalogAccess().has_permission(self._request(True, superuser=True), None))
