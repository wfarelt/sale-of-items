class CompanyMiddleware:
	"""Inyecta request.company desde el usuario autenticado."""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.company = None
		if request.user.is_authenticated and not request.user.is_superuser:
			request.company = request.user.company
		return self.get_response(request)
