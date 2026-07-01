from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.serializers import CourseDetailSerializer, CourseListSerializer
from catalog_extensions.services.course_service import CourseService


class CourseListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = CourseService().list_courses(limit=100)

        serializer = CourseListSerializer(
            [
                {
                    "key": str(course.key),
                    "title": course.title or "",
                    "short_description": course.short_description or "",
                    "marketing_url": course.marketing_url or "",
                }
                for course in courses
            ],
            many=True,
        )

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_key):
        course = CourseService().get_course(course_key)

        if not course:
            return Response(
                {
                    "code": "COURSE_NOT_FOUND",
                    "message": "Course does not exist.",
                },
                status=404,
            )

        serializer = CourseDetailSerializer(
            {
                "key": str(course.key),
                "title": course.title or "",
                "short_description": course.short_description or "",
                "full_description": getattr(course, "full_description", "") or "",
                "marketing_url": course.marketing_url or "",
            }
        )

        return Response(serializer.data)
