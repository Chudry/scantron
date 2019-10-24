from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django_scantron.models import ScheduledScan

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(http_method_names=["GET"])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@login_required(login_url="login")
def retrieve_scan_file(request, id):
    # Lookup result_file_base_name based of scan ID.
    requested_scan = ScheduledScan.objects.get(id=id)

    result_file_base_name = requested_scan.result_file_base_name
    scan_binary = requested_scan.scan_binary

    file_extension = ""

    if scan_binary == "nmap":
        file_extension = "nmap"

    elif scan_binary == "masscan":
        file_extension = "json"

    scan_file = f"{result_file_base_name}.{file_extension}"

    # Serve file using nginx X-Accel-Redirect.
    # https://wellfire.co/learn/nginx-django-x-accel-redirects/
    response = HttpResponse()
    response["Content-Type"] = "text/plain"
    response["Content-Disposition"] = f"inline; filename={scan_file}"
    response["X-Accel-Redirect"] = f"/protected/complete/{scan_file}"

    return response
