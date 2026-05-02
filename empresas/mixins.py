class CompanyQuerysetMixin:
	"""
	Compatibilidad temporal mientras se desmonta el modelo multiempresa.
	"""

	def get_queryset(self):
		return super().get_queryset()

	def form_valid(self, form):
		return super().form_valid(form)
