import hashlib


def get_client_ip(request):
	if request is None:
		return "unknown"

	x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
	if x_forwarded_for:
		return x_forwarded_for.split(",")[0].strip()

	return request.META.get("REMOTE_ADDR", "unknown")


def build_login_lock_key(username, ip_address):
	raw_key = f"{username.lower().strip()}|{ip_address}"
	digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
	return f"login_lock:{digest}"