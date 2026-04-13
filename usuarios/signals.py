import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import LoginEvent, User
from .security import get_client_ip

security_log = logging.getLogger('security')


def _user_agent(request):
    if request is None:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:500]


@receiver(user_logged_in)
def register_login_success(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    LoginEvent.objects.create(
        user=user,
        username=user.username,
        event_type=LoginEvent.EVENT_LOGIN_SUCCESS,
        ip_address=ip,
        user_agent=_user_agent(request),
    )
    security_log.info(
        'LOGIN_SUCCESS username=%s ip=%s',
        user.username, ip,
    )


@receiver(user_logged_out)
def register_logout(sender, request, user, **kwargs):
    if not user:
        return
    ip = get_client_ip(request)
    LoginEvent.objects.create(
        user=user,
        username=user.username,
        event_type=LoginEvent.EVENT_LOGOUT,
        ip_address=ip,
        user_agent=_user_agent(request),
    )
    security_log.info(
        'LOGOUT username=%s ip=%s',
        user.username, ip,
    )


@receiver(user_login_failed)
def register_login_failed(sender, credentials, request, **kwargs):
    username = (credentials or {}).get("username", "")
    ip = get_client_ip(request)
    user = User.objects.filter(username=username).first() if username else None
    LoginEvent.objects.create(
        user=user,
        username=username,
        event_type=LoginEvent.EVENT_LOGIN_FAILED,
        ip_address=ip,
        user_agent=_user_agent(request),
    )
    security_log.warning(
        'LOGIN_FAILED username=%s ip=%s',
        username, ip,
    )