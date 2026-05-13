from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from course_discovery.apps.course_metadata.models import Course
from catalog_extensions.api.serializers import UnifiedCourseSerializer


class UnifiedCatalogView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.all().order_by("key")[:100]

        data = [
            {
                "key": str(course.key),
                "title": course.title or "",
                "short_description": course.short_description or "",
                "marketing_url": course.marketing_url or "",
            }
            for course in courses
        ]

        serializer = UnifiedCourseSerializer(data, many=True)

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )
