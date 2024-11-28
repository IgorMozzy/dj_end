from django.http import HttpResponseForbidden, HttpResponseRedirect
from conf.settings import METRICS_ACCESS_TOKEN


class MetricsTokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/metrics'):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer ' + METRICS_ACCESS_TOKEN):
                return HttpResponseForbidden("Access denied.")

        return self.get_response(request)


class AdminLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin') and not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return self.get_response(request)
