from course_discovery.apps.course_metadata.models import Subject


class SubjectRepository:
    """Repository for Discovery Subject data."""

    def list(self, limit=100):
        return Subject.objects.all()[:limit]

    def get(self, slug):
        return Subject.objects.filter(slug=slug).first()
