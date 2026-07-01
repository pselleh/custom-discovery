from django.http import JsonResponse
from django.urls import path


def not_implemented(request):
    return JsonResponse(
        {"detail": "Subjects endpoint not implemented"},
        status=501,
    )


urlpatterns = [
    path("", not_implemented, name="subjects"),
]
