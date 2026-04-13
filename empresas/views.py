from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
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

	def dispatch(self, request, *args, **kwargs):
		if not getattr(request, "company", None):
			messages.error(request, "No tienes una empresa activa asociada para configurar.")
			return redirect("usuarios:dashboard")
		return super().dispatch(request, *args, **kwargs)

	def get_object(self, queryset=None):
		return self.request.company

	def form_valid(self, form):
		messages.success(self.request, "Datos principales de la empresa actualizados correctamente.")
		return super().form_valid(form)
