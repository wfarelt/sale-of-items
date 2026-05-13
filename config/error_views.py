from django.http import HttpResponseServerError
from django.shortcuts import render


def server_error_view(request):
    show_incident_id = bool(
        getattr(request, "user", None)
        and request.user.is_authenticated
        and request.user.is_superuser
    )
    context = {
        "incident_id": getattr(request, "request_id", "-"),
        "show_incident_id": show_incident_id,
    }
    return HttpResponseServerError(render(request, "errors/500.html", context=context))