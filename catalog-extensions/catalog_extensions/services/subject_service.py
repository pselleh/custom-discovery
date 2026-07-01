from catalog_extensions.repositories.subject_repository import SubjectRepository


class SubjectService:

    def __init__(self):
        self.repository = SubjectRepository()

    def list(self):
        return self.repository.list()

    def get(self, slug):
        return self.repository.get(slug)
