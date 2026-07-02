from course_discovery.apps.course_metadata.models import Program


class ProgramRepository:
    """Repository for Discovery Program data."""

    def _base_queryset(self):
        return (
            Program.objects
            .prefetch_related(
                # Program relationships
                "authoring_organizations",
                "courses",

                # Course relationships
                "courses__subjects",
                "courses__authoring_organizations",

                # CourseRun relationships
                "courses__course_runs",
                "courses__course_runs__seats",
                "courses__course_runs__seats__currency",
                "courses__course_runs__seats__type",
            )
            .order_by("title")
        )

    def list_programs(self, filters=None, limit=100):
        queryset = self._base_queryset()

        filters = filters or {}

        if filters.get("organization"):
            queryset = queryset.filter(
                authoring_organizations__key=filters["organization"]
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

    def get_by_uuid(self, uuid):
        return (
            self._base_queryset()
            .filter(uuid=uuid)
            .first()
        )
