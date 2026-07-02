from catalog_extensions.repositories.program_repository import ProgramRepository


class ProgramService:
    """Service layer for Discovery Programs."""

    def __init__(self):
        self.repository = ProgramRepository()

    def list_programs(self, filters=None, limit=100):
        return self.repository.list_programs(
            filters=filters,
            limit=limit,
        )

    def get_program(self, uuid):
        return self.repository.get_by_uuid(uuid)
