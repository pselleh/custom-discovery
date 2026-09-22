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
                "cba_catalog",
                "cba_course_requirements",
                "cba_course_requirements__course_run",
                "cba_course_requirements__course_run__course",
                "cba_course_requirements__course_run__cba_catalog",
                "cba_course_requirements__course_run__cba_faculty_assignments",
                "cba_course_requirements__course_run__cba_faculty_assignments__person",
                "cba_course_requirements__course_run__seats",
                "cba_course_requirements__course_run__seats__currency",
                "cba_course_requirements__course_run__seats__type",
                "cba_faculty_assignments",
                "cba_faculty_assignments__person",

                # Course relationships
                "courses__subjects",
                "courses__authoring_organizations",

                # CourseRun relationships
                "courses__course_runs",
                "courses__course_runs__cba_catalog",
                "courses__course_runs__cba_faculty_assignments",
                "courses__course_runs__cba_faculty_assignments__person",
                "courses__course_runs__seats",
                "courses__course_runs__seats__currency",
                "courses__course_runs__seats__type",
            )
            .order_by("title")
        )

    def list_programs(self, filters=None, limit=100, public_only=True):
        queryset = self._base_queryset()

        if public_only:
            queryset = queryset.filter(cba_catalog__catalog_visibility="public")

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

        if filters.get("program_code"):
            queryset = queryset.filter(
                cba_catalog__program_code=filters["program_code"]
            )

        if filters.get("catalog_status"):
            queryset = queryset.filter(
                cba_catalog__catalog_status=filters["catalog_status"]
            )

        return queryset.distinct()[:limit]

    def get_by_uuid(self, uuid, public_only=True):
        queryset = self._base_queryset().filter(uuid=uuid)
        if public_only:
            queryset = queryset.filter(cba_catalog__catalog_visibility="public")
        return queryset.first()
