from course_discovery.apps.course_metadata.models import Course


class CourseRepository:
    def list_courses(self, limit=100):
        return (
            Course.objects
            .all()
            .prefetch_related("course_runs")
            .order_by("key")[:limit]
        )

    def get_by_key(self, course_key):
        return (
            Course.objects
            .prefetch_related("course_runs")
            .filter(key=course_key)
            .first()
        )
