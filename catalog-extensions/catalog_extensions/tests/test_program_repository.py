from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from catalog_extensions.repositories.program_repository import (
    ProgramRepository,
)


class ProgramRepositoryFilterTests(SimpleTestCase):
    def _queryset(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        queryset.distinct.return_value = queryset
        queryset.__getitem__.return_value = queryset
        return queryset

    def test_public_category_filter_requires_active_category(
        self,
    ):
        repository = ProgramRepository()
        queryset = self._queryset()

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.list_programs(
                filters={
                    "catalog_category": (
                        "enterprise-risk-management"
                    ),
                },
                public_only=True,
            )

        self.assertEqual(
            queryset.filter.call_args_list,
            [
                call(
                    cba_catalog__catalog_visibility=(
                        "public"
                    )
                ),
                call(
                    cba_catalog__catalog_categories__key=(
                        "enterprise-risk-management"
                    ),
                    cba_catalog__catalog_categories__is_active=(
                        True
                    ),
                ),
            ],
        )

    def test_internal_category_filter_omits_visibility(
        self,
    ):
        repository = ProgramRepository()
        queryset = self._queryset()

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.list_programs(
                filters={
                    "catalog_category": (
                        "organizational-resilience"
                    ),
                },
                public_only=False,
            )

        queryset.filter.assert_called_once_with(
            cba_catalog__catalog_categories__key=(
                "organizational-resilience"
            ),
            cba_catalog__catalog_categories__is_active=True,
        )

    def test_category_and_status_filters_are_both_applied(
        self,
    ):
        repository = ProgramRepository()
        queryset = self._queryset()

        with patch.object(
            repository,
            "_base_queryset",
            return_value=queryset,
        ):
            repository.list_programs(
                filters={
                    "catalog_status": "waitlist_open",
                    "catalog_category": (
                        "organizational-resilience"
                    ),
                },
                public_only=False,
            )

        self.assertEqual(
            queryset.filter.call_args_list,
            [
                call(
                    cba_catalog__catalog_status=(
                        "waitlist_open"
                    )
                ),
                call(
                    cba_catalog__catalog_categories__key=(
                        "organizational-resilience"
                    ),
                    cba_catalog__catalog_categories__is_active=(
                        True
                    ),
                ),
            ],
        )
