from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.serializers.organization import (
    OrganizationSerializer,
)
from catalog_extensions.services.organization_service import (
    OrganizationService,
)


class OrganizationListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        organizations = OrganizationService().list()

        serializer = OrganizationSerializer(
            organizations,
            many=True,
        )

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )
