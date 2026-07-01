from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.serializers.subject import SubjectSerializer
from catalog_extensions.services.subject_service import SubjectService


class SubjectListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        subjects = SubjectService().list()

        serializer = SubjectSerializer(
            subjects,
            many=True,
        )

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )
