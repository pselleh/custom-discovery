from catalog_extensions.repositories.organization_repository import (
    OrganizationRepository,
)


class OrganizationService:

    def __init__(self):
        self.repository = OrganizationRepository()

    def list(self):
        return self.repository.list()

    def get(self, key):
        return self.repository.get(key)
