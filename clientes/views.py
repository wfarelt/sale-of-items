from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView
from django.utils import timezone

from config.pdf_utils import render_to_pdf
from empresas.models import Company
from ventas.models import Sale, Payment

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


class ClientLookupView(ClientAccessMixin, View):
	def get(self, request, *args, **kwargs):
		query = request.GET.get("q", "").strip()
		clients_qs = Client.objects.filter(is_active=True)

		if query:
			clients_qs = clients_qs.filter(
				Q(name__icontains=query)
				| Q(nit_ci__icontains=query)
				| Q(phone__icontains=query)
				| Q(email__icontains=query)
			)

		clients = list(clients_qs.order_by("name")[:20])
		data = [
			{
				"id": client.id,
				"name": client.name,
				"nit_ci": client.nit_ci,
				"phone": client.phone or "",
				"email": client.email or "",
				"label": f"{client.name} ({client.nit_ci})",
			}
			for client in clients
		]
		return JsonResponse({"results": data})


class ClientQuickCreateView(ClientAccessMixin, View):
	def post(self, request, *args, **kwargs):
		name = request.POST.get("name", "").strip()
		nit_ci = request.POST.get("nit_ci", "").strip()
		phone = request.POST.get("phone", "").strip()
		email = request.POST.get("email", "").strip()
		address = request.POST.get("address", "").strip()

		if not name or not nit_ci:
			return JsonResponse(
				{"ok": False, "message": "Nombre y NIT/CI son obligatorios."},
				status=400,
			)

		try:
			client = Client.objects.create(
				name=name,
				nit_ci=nit_ci,
				phone=phone,
				email=email,
				address=address,
				is_active=True,
			)
		except IntegrityError:
			return JsonResponse(
				{"ok": False, "message": "Ya existe un cliente con ese NIT/CI."},
				status=400,
			)

		return JsonResponse(
			{
				"ok": True,
				"client": {
					"id": client.id,
					"name": client.name,
					"nit_ci": client.nit_ci,
					"label": f"{client.name} ({client.nit_ci})",
				},
			}
		)


class AccountStatementView(ClientAccessMixin, DetailView):
	model = Client
	template_name = "clientes/account_statement.html"
	context_object_name = "client"

	def get_context_data(self, **kwargs):
		client = self.get_object()
		# ventas del cliente con pagos prefeteched
		sales_qs = (
			Sale.objects.filter(client=client).exclude(status=Sale.STATUS_PROFORMA)
			.select_related("commercial_condition", "seller")
			.prefetch_related("payments")
			.order_by("-date")
		)
		sales_data = []
		total_pending = 0
		total_billed = 0
		total_paid_sum = 0
		for s in sales_qs:
			paid = s.total_paid
			pending = s.pending_balance
			total_pending += pending
			total_billed += s.total or 0
			total_paid_sum += paid
			sales_data.append({"sale": s, "total": s.total, "paid": paid, "pending": pending, "due_date": s.due_date})

		payments = Payment.objects.filter(sale__client=client).select_related("method", "sale").order_by("-paid_at")

		context = super().get_context_data(**kwargs)
		context.update({
			"sales_data": sales_data,
			"payments": payments,
			"total_pending": total_pending,
			"total_billed": total_billed,
			"total_paid_sum": total_paid_sum,
			"generated_at": timezone.now(),
			"company": Company.get_solo(),
		})
		return context


class AccountStatementPdfView(ClientAccessMixin, View):
	def get(self, request, pk, *args, **kwargs):
		client = get_object_or_404(Client, pk=pk)

		# Recompute context similarly to AccountStatementView
		sales_qs = (
			Sale.objects.filter(client=client).exclude(status=Sale.STATUS_PROFORMA)
			.select_related("commercial_condition", "seller")
			.prefetch_related("payments")
			.order_by("-date")
		)
		sales_data = []
		total_pending = 0
		total_billed = 0
		total_paid_sum = 0
		for s in sales_qs:
			paid = s.total_paid
			pending = s.pending_balance
			total_pending += pending
			total_billed += s.total or 0
			total_paid_sum += paid
			sales_data.append({"sale": s, "total": s.total, "paid": paid, "pending": pending, "due_date": s.due_date})

		payments = Payment.objects.filter(sale__client=client).select_related("method", "sale").order_by("-paid_at")

		context = {
			"client": client,
			"sales_data": sales_data,
			"payments": payments,
			"total_pending": total_pending,
			"total_billed": total_billed,
			"total_paid_sum": total_paid_sum,
			"generated_at": timezone.now(),
			"company": Company.get_solo(),
		}

		filename = f"estado_cliente_{client.nit_ci}.pdf"
		base_url = request.build_absolute_uri("/")
		return render_to_pdf("clientes/account_statement_pdf.html", context, filename=filename, base_url=base_url)

