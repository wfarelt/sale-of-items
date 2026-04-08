from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class ClientAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		user = self.request.user
		return user.is_admin or user.is_vendedor


class ClientListView(ClientAccessMixin, ListView):
	model = Client
	template_name = "clientes/client_list.html"
	context_object_name = "clients"
	paginate_by = 10

	def get_queryset(self):
		queryset = super().get_queryset()
		search = self.request.GET.get("q", "").strip()

		if search:
			queryset = queryset.filter(
				Q(name__icontains=search)
				| Q(nit_ci__icontains=search)
				| Q(phone__icontains=search)
				| Q(email__icontains=search)
			)

		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "").strip()
		return context


class ClientCreateView(ClientAccessMixin, CreateView):
	model = Client
	form_class = ClientForm
	template_name = "clientes/client_form.html"
	success_url = reverse_lazy("clientes:list")


class ClientUpdateView(ClientAccessMixin, UpdateView):
	model = Client
	form_class = ClientForm
	template_name = "clientes/client_form.html"
	success_url = reverse_lazy("clientes:list")


class ClientDeleteView(ClientAccessMixin, DeleteView):
	model = Client
	template_name = "clientes/client_confirm_delete.html"
	success_url = reverse_lazy("clientes:list")

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.is_active = not self.object.is_active
		self.object.save(update_fields=["is_active", "updated_at"])
		if self.object.is_active:
			messages.success(request, "Cliente activado correctamente.")
		else:
			messages.warning(request, "Cliente desactivado correctamente.")
		return redirect(self.success_url)
