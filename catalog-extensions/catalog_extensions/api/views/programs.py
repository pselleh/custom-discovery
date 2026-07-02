from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.pagination import CBAPagination
from catalog_extensions.api.serializers import ProgramSerializer
from catalog_extensions.services.program_service import ProgramService


class ProgramListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {
            "organization": request.query_params.get("organization"),
            "title": request.query_params.get("title"),
            "uuid": request.query_params.get("uuid"),
        }

        queryset = ProgramService().list_programs(
            filters=filters,
        )

        paginator = CBAPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self,
        )

        serializer = ProgramSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class ProgramDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uuid):
        service = ProgramService()

        program = service.get_program(uuid)

        if not program:
            return Response(
                {
                    "code": "PROGRAM_NOT_FOUND",
                    "message": "Program does not exist.",
                },
                status=404,
            )

        serializer = ProgramSerializer(program)

        return Response(serializer.data)
