from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.pagination import CBAPagination
from catalog_extensions.api.permissions import HasRestrictedCatalogAccess
from catalog_extensions.api.serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
)
from catalog_extensions.services.course_service import CourseService


class CourseListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {
            "organization": request.query_params.get("organization"),
            "subject": request.query_params.get("subject"),
            "title": request.query_params.get("title"),
            "uuid": request.query_params.get("uuid"),
            "catalog_status": request.query_params.get("catalog_status"),
        }

        queryset = CourseService().list_courses(
            filters=filters,
        )

        paginator = CBAPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self,
        )

        serializer = CourseListSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_key):
        service = CourseService()

        course = service.get_course(course_key)

        if not course:
            return Response(
                {
                    "code": "COURSE_NOT_FOUND",
                    "message": "Course does not exist.",
                },
                status=404,
            )

        serializer = CourseDetailSerializer(course)

        return Response(serializer.data)


class InternalCourseListView(CourseListView):
    """Authenticated Wagtail endpoint that can return hidden catalog records."""

    permission_classes = [HasRestrictedCatalogAccess]

    def get(self, request):
        filters = {
            "organization": request.query_params.get("organization"),
            "subject": request.query_params.get("subject"),
            "title": request.query_params.get("title"),
            "uuid": request.query_params.get("uuid"),
            "catalog_status": request.query_params.get("catalog_status"),
        }
        queryset = CourseService().list_courses(filters=filters, public_only=False)
        paginator = CBAPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(CourseListSerializer(page, many=True).data)


class InternalCourseDetailView(CourseDetailView):
    permission_classes = [HasRestrictedCatalogAccess]

    def get(self, request, course_key):
        course = CourseService().get_course(course_key, public_only=False)
        if not course:
            return Response(
                {"code": "COURSE_NOT_FOUND", "message": "Course does not exist."},
                status=404,
            )
        return Response(CourseDetailSerializer(course).data)
