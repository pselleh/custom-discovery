from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.serializers import CourseDetailSerializer, CourseListSerializer
from catalog_extensions.services.course_service import CourseService


class CourseListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        service = CourseService()
        courses = service.list_courses(limit=100)

        serializer = CourseListSerializer(
            [service.serialize_course(course) for course in courses],
            many=True,
        )

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


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

        serializer = CourseDetailSerializer(service.serialize_course(course))
        return Response(serializer.data)
