from course_discovery.apps.course_metadata.models import Course


class CourseRepository:
    """Repository for Discovery Course data."""

    def _base_queryset(self):
        """Return the shared queryset for course operations."""
        return (
            Course.objects
            .prefetch_related(
                "authoring_organizations",
                "subjects",
                "course_runs",
                "course_runs__cba_catalog",
                (
                    "course_runs__cba_catalog__"
                    "primary_catalog_category"
                ),
                (
                    "course_runs__cba_catalog__"
                    "catalog_categories"
                ),
                "course_runs__cba_faculty_assignments",
                (
                    "course_runs__cba_faculty_assignments__"
                    "person"
                ),
                "course_runs__seats",
                "course_runs__seats__type",
                "course_runs__seats__currency",
            )
            .order_by("key")
        )

    def list_courses(
        self,
        filters=None,
        limit=100,
        public_only=True,
    ):
        queryset = self._base_queryset()
        filters = filters or {}

        if filters.get("organization"):
            queryset = queryset.filter(
                authoring_organizations__key=(
                    filters["organization"]
                )
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

        # Keep every CourseRun-specific condition in one
        # filter call. This prevents visibility, status, and
        # category from being satisfied by different runs.
        course_run_filters = {}

        if public_only:
            course_run_filters[
                "course_runs__cba_catalog__catalog_visibility"
            ] = "public"

        if filters.get("catalog_status"):
            course_run_filters[
                "course_runs__cba_catalog__catalog_status"
            ] = filters["catalog_status"]

        if filters.get("catalog_category"):
            course_run_filters[
                (
                    "course_runs__cba_catalog__"
                    "catalog_categories__key"
                )
            ] = filters["catalog_category"]

            course_run_filters[
                (
                    "course_runs__cba_catalog__"
                    "catalog_categories__is_active"
                )
            ] = True

        if course_run_filters:
            queryset = queryset.filter(
                **course_run_filters
            )

        return queryset.distinct()[:limit]

    def get_by_key(
        self,
        course_key,
        public_only=True,
    ):
        queryset = self._base_queryset()

        if str(course_key).startswith("course-v1:"):
            course_run_filters = {
                "course_runs__key": course_key,
            }

            if public_only:
                course_run_filters[
                    (
                        "course_runs__cba_catalog__"
                        "catalog_visibility"
                    )
                ] = "public"

            return (
                queryset
                .filter(**course_run_filters)
                .distinct()
                .first()
            )

        queryset = queryset.filter(key=course_key)

        if public_only:
            queryset = queryset.filter(
                course_runs__cba_catalog__catalog_visibility=(
                    "public"
                )
            )

        return queryset.distinct().first()
