class CompanyQuerysetMixin:
	"""
	Filtra automáticamente los querysets por la empresa del usuario autenticado.
	El superadmin (sin company) ve todos los datos.
	"""

	def get_queryset(self):
		qs = super().get_queryset()
		company = getattr(self.request, 'company', None)
		if company:
			return qs.filter(company=company)
		return qs

	def form_valid(self, form):
		if hasattr(form.instance, 'company_id') and not form.instance.company_id:
			form.instance.company = self.request.company
		return super().form_valid(form)
