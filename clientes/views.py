from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
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
