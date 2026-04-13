import logging
import time
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

security_log = logging.getLogger('security')


class SessionInactivityMiddleware:
	"""Logs out authenticated users after a period of inactivity."""

	SESSION_ACTIVITY_KEY = "session_last_activity_ts"

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.user.is_authenticated:
			timeout_seconds = max(0, int(getattr(settings, "SESSION_INACTIVITY_TIMEOUT", 0)))
			current_ts = int(time.time())
			last_activity = request.session.get(self.SESSION_ACTIVITY_KEY)

			if timeout_seconds > 0 and last_activity and (current_ts - int(last_activity)) > timeout_seconds:
				next_path = request.get_full_path()
				username = request.user.username
				logout(request)
				security_log.info(
					'SESSION_EXPIRED username=%s ip=%s path=%s',
					username,
					request.META.get('REMOTE_ADDR', 'unknown'),
					next_path,
				)
				messages.warning(request, "Tu sesion expiro por inactividad. Inicia sesion nuevamente.")
				login_url = resolve_url(settings.LOGIN_URL)
				query = urlencode({"next": next_path})
				return HttpResponseRedirect(f"{login_url}?{query}")

			request.session[self.SESSION_ACTIVITY_KEY] = current_ts

		return self.get_response(request)