from course_discovery.apps.course_metadata.models import Course


class CourseRepository:
    """Repository for Discovery Course data."""

    def _base_queryset(self):
        """
        Shared queryset for all course operations.
        """
        return (
            Course.objects
            .prefetch_related(
                "authoring_organizations",
                "subjects",
                "course_runs",
                "course_runs__seats",
                "course_runs__seats__type",
                "course_runs__seats__currency",
            )
            .order_by("key")
        )

    def list_courses(self, filters=None, limit=100):
        queryset = self._base_queryset()

        filters = filters or {}

        if filters.get("organization"):
            queryset = queryset.filter(
                authoring_organizations__key=filters["organization"]
            )

        if filters.get("subject"):
            queryset = queryset.filter(
                subjects__slug=filters["subject"]
            )

        if filters.get("title"):
            queryset = queryset.filter(
                title__icontains=filters["title"]
            )

        if filters.get("uuid"):
            queryset = queryset.filter(
                uuid=filters["uuid"]
            )

        return queryset.distinct()[:limit]

    def get_by_key(self, course_key):
        return (
            self._base_queryset()
            .filter(key=course_key)
            .first()
        )
