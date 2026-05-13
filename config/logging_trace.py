import logging
import uuid
from contextvars import ContextVar


app_log = logging.getLogger("app")

_request_context: ContextVar[dict] = ContextVar("request_context", default={})


def _set_request_context(**values):
    context = dict(_request_context.get())
    context.update(values)
    _request_context.set(context)


class RequestContextFilter(logging.Filter):
    """Inject request metadata into log records when available."""

    def filter(self, record):
        context = _request_context.get()
        record.request_id = context.get("request_id", "-")
        record.path = context.get("path", "-")
        record.method = context.get("method", "-")
        record.ip = context.get("ip", "-")
        record.username = context.get("username", "anonymous")
        return True


class RequestTraceMiddleware:
    """Capture per-request metadata and log unexpected server-side failures."""

    REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
    RESPONSE_REQUEST_ID_HEADER = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def __call__(self, request):
        request_id = request.META.get(self.REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
        request.request_id = request_id
        username = "anonymous"

        if getattr(request, "user", None) and request.user.is_authenticated:
            username = request.user.get_username()

        _set_request_context(
            request_id=request_id,
            path=request.get_full_path(),
            method=request.method,
            ip=self._client_ip(request),
            username=username,
        )

        try:
            response = self.get_response(request)
        except Exception:
            app_log.exception("UNHANDLED_EXCEPTION")
            _request_context.set({})
            raise

        if getattr(request, "user", None) and request.user.is_authenticated:
            _set_request_context(username=request.user.get_username())

        if response.status_code >= 500:
            app_log.error("SERVER_ERROR_RESPONSE status_code=%s", response.status_code)

        response[self.RESPONSE_REQUEST_ID_HEADER] = request_id
        _request_context.set({})
        return response