from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.pagination import CBAPagination
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
