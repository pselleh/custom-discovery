from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from catalog_extensions.api.views.courses import (
    CourseListView,
    InternalCourseListView,
)
from catalog_extensions.api.views.programs import (
    InternalProgramListView,
    ProgramListView,
)


class CatalogCategoryViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def _request(self):
        return Request(
            self.factory.get(
                "/catalog/",
                {
                    "catalog_category": (
                        "organizational-resilience"
                    ),
                },
            )
        )

    def _paginator(self, paginator_class):
        paginator = MagicMock()
        paginator.paginate_queryset.return_value = []
        paginator.get_paginated_response.return_value = (
            Response([])
        )
        paginator_class.return_value = paginator
        return paginator

    @patch(
        "catalog_extensions.api.views.courses."
        "CourseListSerializer"
    )
    @patch(
        "catalog_extensions.api.views.courses."
        "CBAPagination"
    )
    @patch(
        "catalog_extensions.api.views.courses."
        "CourseService"
    )
    def test_public_course_view_forwards_category(
        self,
        service_class,
        paginator_class,
        serializer_class,
    ):
        service = service_class.return_value
        service.list_courses.return_value = []
        self._paginator(paginator_class)
        serializer_class.return_value.data = []

        CourseListView().get(self._request())

        filters = service.list_courses.call_args.kwargs[
            "filters"
        ]
        self.assertEqual(
            filters["catalog_category"],
            "organizational-resilience",
        )
        self.assertNotIn(
            "public_only",
            service.list_courses.call_args.kwargs,
        )

    @patch(
        "catalog_extensions.api.views.courses."
        "CourseListSerializer"
    )
    @patch(
        "catalog_extensions.api.views.courses."
        "CBAPagination"
    )
    @patch(
        "catalog_extensions.api.views.courses."
        "CourseService"
    )
    def test_internal_course_view_forwards_category(
        self,
        service_class,
        paginator_class,
        serializer_class,
    ):
        service = service_class.return_value
        service.list_courses.return_value = []
        self._paginator(paginator_class)
        serializer_class.return_value.data = []

        InternalCourseListView().get(self._request())

        service.list_courses.assert_called_once()
        filters = service.list_courses.call_args.kwargs[
            "filters"
        ]
        self.assertEqual(
            filters["catalog_category"],
            "organizational-resilience",
        )
        self.assertFalse(
            service.list_courses.call_args.kwargs[
                "public_only"
            ]
        )

    @patch(
        "catalog_extensions.api.views.programs."
        "ProgramSerializer"
    )
    @patch(
        "catalog_extensions.api.views.programs."
        "CBAPagination"
    )
    @patch(
        "catalog_extensions.api.views.programs."
        "ProgramService"
    )
    def test_public_program_view_forwards_category(
        self,
        service_class,
        paginator_class,
        serializer_class,
    ):
        service = service_class.return_value
        service.list_programs.return_value = []
        self._paginator(paginator_class)
        serializer_class.return_value.data = []

        ProgramListView().get(self._request())

        filters = service.list_programs.call_args.kwargs[
            "filters"
        ]
        self.assertEqual(
            filters["catalog_category"],
            "organizational-resilience",
        )
        self.assertNotIn(
            "public_only",
            service.list_programs.call_args.kwargs,
        )

    @patch(
        "catalog_extensions.api.views.programs."
        "ProgramSerializer"
    )
    @patch(
        "catalog_extensions.api.views.programs."
        "CBAPagination"
    )
    @patch(
        "catalog_extensions.api.views.programs."
        "ProgramService"
    )
    def test_internal_program_view_forwards_category(
        self,
        service_class,
        paginator_class,
        serializer_class,
    ):
        service = service_class.return_value
        service.list_programs.return_value = []
        self._paginator(paginator_class)
        serializer_class.return_value.data = []

        InternalProgramListView().get(self._request())

        service.list_programs.assert_called_once()
        filters = service.list_programs.call_args.kwargs[
            "filters"
        ]
        self.assertEqual(
            filters["catalog_category"],
            "organizational-resilience",
        )
        self.assertFalse(
            service.list_programs.call_args.kwargs[
                "public_only"
            ]
        )
