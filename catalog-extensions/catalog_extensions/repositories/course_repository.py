from course_discovery.apps.course_metadata.models import Course


class CourseRepository:
    """Repository for Discovery Course data."""

    def list_courses(self, limit=100):
        return (
            Course.objects
            .all()
            .order_by("key")[:limit]
        )

    def get_by_key(self, course_key):
        return Course.objects.filter(key=course_key).first()
