from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import CompanySettingsForm
from .models import Company


class CompanySettingsAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin


class CompanySettingsUpdateView(CompanySettingsAccessMixin, UpdateView):
	model = Company
	form_class = CompanySettingsForm
	template_name = "empresas/company_settings_form.html"
	success_url = reverse_lazy("empresas:settings")

	def get_object(self, queryset=None):
		company = Company.get_solo()
		if company:
			return company
		return Company.objects.create(name="Venta de Porcelanatos")

	def form_valid(self, form):
		messages.success(self.request, "Datos principales del negocio actualizados correctamente.")
		return super().form_valid(form)
