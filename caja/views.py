from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView

from .forms import CashBoxCloseForm, CashBoxForm, CashBoxOpeningForm
from .models import CashBox, CashBoxClosure


class CashBoxAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_vendedor


class CashBoxAdminAccessMixin(CashBoxAccessMixin):
	def test_func(self):
		return self.request.user.is_admin


class CashBoxListView(CashBoxAccessMixin, ListView):
	model = CashBox
	template_name = "caja/cashbox_list.html"
	context_object_name = "entries"
	paginate_by = 20

	def get_selected_date(self):
		value = self.request.GET.get("date")
		if value:
			try:
				return date.fromisoformat(value)
			except ValueError:
				pass
		return timezone.localdate()

	def get_queryset(self):
		selected_date = self.get_selected_date()
		queryset = CashBox.objects.filter(date__date=selected_date)
		search = self.request.GET.get("q")
		entry_type = self.request.GET.get("type")
		reference = self.request.GET.get("reference")
		payment_method = self.request.GET.get("payment_method")

		if search:
			queryset = queryset.filter(description__icontains=search)
		if entry_type:
			queryset = queryset.filter(type=entry_type)
		if reference:
			queryset = queryset.filter(reference=reference)
		if payment_method:
			queryset = queryset.filter(payment_method=payment_method)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		selected_date = self.get_selected_date()
		selected_payment_method = self.request.GET.get("payment_method", "")
		filtered_queryset = self.get_queryset()
		date_queryset = CashBox.objects.filter(date__date=selected_date)
		ingresos = filtered_queryset.filter(type=CashBox.TYPE_INCOME).aggregate(total=Sum("amount"))["total"] or 0
		egresos = filtered_queryset.filter(type=CashBox.TYPE_EXPENSE).aggregate(total=Sum("amount"))["total"] or 0
		daily_summary = CashBoxClosure.get_day_summary(selected_date)

		report_payment_methods = [
			CashBox.PAYMENT_METHOD_CASH,
			CashBox.PAYMENT_METHOD_QR,
			CashBox.PAYMENT_METHOD_TRANSFER,
		]
		method_label_map = dict(CashBox.PAYMENT_METHOD_CHOICES)
		method_report = []
		for method_key in report_payment_methods:
			income_by_method = date_queryset.filter(type=CashBox.TYPE_INCOME, payment_method=method_key).aggregate(total=Sum("amount"))["total"] or 0
			expense_by_method = date_queryset.filter(type=CashBox.TYPE_EXPENSE, payment_method=method_key).aggregate(total=Sum("amount"))["total"] or 0
			method_report.append(
				{
					"key": method_key,
					"label": method_label_map.get(method_key, method_key),
					"income": income_by_method,
					"expense": expense_by_method,
					"net": income_by_method - expense_by_method,
				}
			)

		context.update(
			{
				"selected_date": selected_date,
				"search_query": self.request.GET.get("q", ""),
				"selected_type": self.request.GET.get("type", ""),
				"selected_reference": self.request.GET.get("reference", ""),
				"selected_payment_method": selected_payment_method,
				"type_choices": CashBox.TYPE_CHOICES,
				"reference_choices": CashBox.REFERENCE_CHOICES,
				"payment_method_choices": CashBox.PAYMENT_METHOD_CHOICES,
				"method_report": method_report,
				"income_total": ingresos,
				"expense_total": egresos,
				"balance_total": daily_summary["current_balance"],
				"opening_balance": daily_summary["opening_balance"],
				"is_day_closed": daily_summary["is_closed"],
				"closed_at": daily_summary["closed_at"],
				"closing_balance": daily_summary["closing_balance"],
			}
		)
		return context


class CashBoxDetailView(CashBoxAccessMixin, DetailView):
	model = CashBox
	template_name = "caja/cashbox_detail.html"
	context_object_name = "entry"


class CashBoxCreateView(CashBoxAccessMixin, CreateView):
	model = CashBox
	form_class = CashBoxForm
	template_name = "caja/cashbox_form.html"
	success_url = reverse_lazy("caja:list")

	def get_initial(self):
		initial = super().get_initial()
		selected_date = self.request.GET.get("date")
		if selected_date:
			initial["date"] = f"{selected_date}T08:00"
		return initial

	def get_success_url(self):
		entry_date = CashBox.resolve_business_date(self.object.date)
		return f'{reverse_lazy("caja:list")}?date={entry_date.isoformat()}'

	def form_valid(self, form):
		messages.success(self.request, "Movimiento de caja registrado exitosamente.")
		return super().form_valid(form)


class CashBoxOpeningView(CashBoxAccessMixin, FormView):
	form_class = CashBoxOpeningForm
	template_name = "caja/cashbox_opening_form.html"
	success_url = reverse_lazy("caja:list")

	def get_initial(self):
		initial = super().get_initial()
		selected_date = self.request.GET.get("date")
		try:
			target_date = date.fromisoformat(selected_date) if selected_date else timezone.localdate()
		except ValueError:
			target_date = timezone.localdate()
		summary = CashBoxClosure.get_day_summary(target_date)
		initial["date"] = target_date
		initial["opening_balance"] = summary["opening_balance"]
		return initial

	def form_valid(self, form):
		try:
			closure = CashBoxClosure.set_opening_balance(
				target_date=form.cleaned_data["date"],
				opening_balance=form.cleaned_data["opening_balance"],
			)
		except ValidationError as exc:
			form.add_error(None, exc)
			return self.form_invalid(form)

		messages.success(self.request, f"Saldo inicial actualizado para el {closure.date.strftime('%d/%m/%Y')}.")
		return HttpResponseRedirect(f'{reverse_lazy("caja:list")}?date={closure.date.isoformat()}')


class CashBoxCloseView(CashBoxAccessMixin, FormView):
	form_class = CashBoxCloseForm
	template_name = "caja/cashbox_close_form.html"
	success_url = reverse_lazy("caja:list")

	def get_initial(self):
		initial = super().get_initial()
		selected_date = self.request.GET.get("date")
		try:
			initial["date"] = date.fromisoformat(selected_date) if selected_date else timezone.localdate()
		except ValueError:
			initial["date"] = timezone.localdate()
		return initial

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = context["form"]
		if form.is_bound and form.is_valid():
			target_date = form.cleaned_data["date"]
		else:
			target_date = form.initial.get("date", timezone.localdate())
		context["target_date"] = target_date
		context["summary"] = CashBoxClosure.get_day_summary(target_date)
		return context

	def form_valid(self, form):
		target_date = form.cleaned_data["date"]
		closure, _ = CashBoxClosure.objects.get_or_create(
			date=target_date,
			defaults={
				"opening_balance": CashBoxClosure.get_suggested_opening_balance(target_date),
				"closing_balance": CashBoxClosure.get_suggested_opening_balance(target_date),
			},
		)
		try:
			closure.perform_close()
		except ValidationError as exc:
			form.add_error(None, exc)
			return self.form_invalid(form)

		messages.success(self.request, f"Caja cerrada para el {closure.date.strftime('%d/%m/%Y')}.")
		return HttpResponseRedirect(f'{reverse_lazy("caja:list")}?date={closure.date.isoformat()}')


class CashBoxDeleteView(CashBoxAdminAccessMixin, DeleteView):
	model = CashBox
	template_name = "caja/cashbox_confirm_delete.html"
	success_url = reverse_lazy("caja:list")

	def get_success_url(self):
		entry_date = CashBox.resolve_business_date(self.object.date)
		return f'{reverse_lazy("caja:list")}?date={entry_date.isoformat()}'

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		try:
			CashBox.validate_day_open(self.object.date)
		except ValidationError as exc:
			messages.error(request, str(exc))
			return redirect(self.get_success_url())

		messages.warning(request, "Movimiento de caja eliminado.")
		return super().post(request, *args, **kwargs)

	def handle_no_permission(self):
		messages.error(self.request, "Solo los administradores pueden eliminar movimientos de caja.")
		return redirect(self.success_url)
