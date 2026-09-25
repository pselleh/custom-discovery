from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from catalog_extensions.repositories.course_repository import (
    CourseRepository,
)


class CourseRepositoryFilterTests(SimpleTestCase):
    def test_public_status_and_category_share_one_filter(
        self,
    ):
        repository = CourseRepository()
        queryset = MagicMock()

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.list_courses(
                filters={
                    "catalog_status": "waitlist_open",
                    "catalog_category": (
                        "organizational-resilience"
                    ),
                },
                limit=25,
                public_only=True,
            )

        queryset.filter.assert_called_once_with(
            course_runs__cba_catalog__catalog_visibility=(
                "public"
            ),
            course_runs__cba_catalog__catalog_status=(
                "waitlist_open"
            ),
            course_runs__cba_catalog__catalog_categories__key=(
                "organizational-resilience"
            ),
            course_runs__cba_catalog__catalog_categories__is_active=(
                True
            ),
        )

    def test_internal_category_filter_omits_visibility(
        self,
    ):
        repository = CourseRepository()
        queryset = MagicMock()

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.list_courses(
                filters={
                    "catalog_category": (
                        "enterprise-risk-management"
                    ),
                },
                public_only=False,
            )

        queryset.filter.assert_called_once_with(
            course_runs__cba_catalog__catalog_categories__key=(
                "enterprise-risk-management"
            ),
            course_runs__cba_catalog__catalog_categories__is_active=(
                True
            ),
        )

    def test_course_run_key_and_visibility_share_filter(
        self,
    ):
        repository = CourseRepository()
        queryset = MagicMock()
        course_key = (
            "course-v1:CBA+ORF101M01C01+2027"
        )

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.get_by_key(
                course_key,
                public_only=True,
            )

        queryset.filter.assert_called_once_with(
            course_runs__key=course_key,
            course_runs__cba_catalog__catalog_visibility=(
                "public"
            ),
        )
