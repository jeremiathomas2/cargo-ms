import threading

from django.http import HttpResponse

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        return None


class ClearThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response


class SuppressViteClientRequestsMiddleware:
    """
    Dev-only helper. Browser extensions / stale service workers sometimes
    inject a <script src="/@vite/client"> tag on 127.0.0.1 pages — those
    produce a noisy 404 log line. Catch the request super early and reply
    with 204 No-Content so no warning is emitted and the in-page script
    silently short-circuits (no 404 body = HMR handshake aborts).
    """

    VITE_PREFIXES = ("/@vite/", "/@react-refresh", "/__vite_ping", "/@id/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        for prefix in self.VITE_PREFIXES:
            if path.startswith(prefix):
                return HttpResponse(status=204)
        return self.get_response(request)
