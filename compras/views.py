from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from empresas.mixins import CompanyQuerysetMixin
from .models import Purchase
from .forms import PurchaseForm, PurchaseDetailFormSet


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""Acceso solo para Admin y Almacén"""
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class PurchaseListView(InventoryAccessMixin, CompanyQuerysetMixin, ListView):
	model = Purchase
	template_name = "compras/purchase_list.html"
	context_object_name = "purchases"
	paginate_by = 20

	def get_queryset(self):
		queryset = super().get_queryset()
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(supplier__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		return context


class PurchaseDetailView(InventoryAccessMixin, CompanyQuerysetMixin, DetailView):
	model = Purchase
	template_name = "compras/purchase_detail.html"
	context_object_name = "purchase"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["details"] = self.object.purchasedetail_set.select_related("product").all()
		return context


class PurchaseCreateView(InventoryAccessMixin, CompanyQuerysetMixin, CreateView):
	model = Purchase
	form_class = PurchaseForm
	template_name = "compras/purchase_form.html"
	success_url = reverse_lazy("compras:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = PurchaseDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save(commit=False)
			self.object.company = request.company
			self.object.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			# Actualizar stock si es "recibida"
			if self.object.status == "recibida":
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date, self.object.company)
				self.object.apply_inventory_update()
				CashBox.register_purchase(self.object)

			messages.success(request, "Compra registrada exitosamente.")
			return redirect(self.success_url)
		else:
			return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = PurchaseDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = PurchaseDetailFormSet(instance=self.object)
		return super().get_context_data(**kwargs)


class PurchaseUpdateView(InventoryAccessMixin, CompanyQuerysetMixin, UpdateView):
	model = Purchase
	form_class = PurchaseForm
	template_name = "compras/purchase_form.html"
	success_url = reverse_lazy("compras:list")

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if not self.object.is_editable():
			messages.warning(request, "Esta compra ya no puede editarse porque su estado no es Pendiente.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if not self.object.is_editable():
			messages.warning(request, "Esta compra ya no puede editarse porque su estado no es Pendiente.")
			return redirect(self.success_url)

		old_status = self.object.status

		form = self.get_form()
		formset = PurchaseDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			# Si cambió a "recibida" desde otro estado, actualizar stock
			if old_status != "recibida" and self.object.status == "recibida":
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date, self.object.company)
				self.object.apply_inventory_update()
				CashBox.register_purchase(self.object)
				messages.info(request, f"Stock actualizado: +{sum(d.quantity for d in self.object.purchasedetail_set.all())} unidades.")

			messages.success(request, "Compra actualizada exitosamente.")
			return redirect(self.success_url)
		else:
			return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = PurchaseDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = PurchaseDetailFormSet(instance=self.object)
		kwargs["purchase_locked"] = bool(self.object and not self.object.is_editable())
		return super().get_context_data(**kwargs)


class PurchaseDeleteView(InventoryAccessMixin, CompanyQuerysetMixin, DeleteView):
	model = Purchase
	template_name = "compras/purchase_confirm_delete.html"
	success_url = reverse_lazy("compras:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status == "recibida":
			from caja.models import CashBox
			try:
				CashBox.validate_day_open(company=self.object.company)
				self.object.revert_inventory_update()
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			CashBox.register_purchase_reversal(self.object)
			messages.warning(request, "Compra eliminada y stock revertido.")
		else:
			messages.warning(request, "Compra eliminada.")
		return super().post(request, *args, **kwargs)



class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	"""Acceso solo para Admin y Almacén"""
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class PurchaseListView(InventoryAccessMixin, ListView):
	model = Purchase
	template_name = "compras/purchase_list.html"
	context_object_name = "purchases"
	paginate_by = 20

	def get_queryset(self):
		queryset = Purchase.objects.all()
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(supplier__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		return context


class PurchaseDetailView(InventoryAccessMixin, DetailView):
	model = Purchase
	template_name = "compras/purchase_detail.html"
	context_object_name = "purchase"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["details"] = self.object.purchasedetail_set.select_related("product").all()
		return context


class PurchaseCreateView(InventoryAccessMixin, CreateView):
	model = Purchase
	form_class = PurchaseForm
	template_name = "compras/purchase_form.html"
	success_url = reverse_lazy("compras:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = PurchaseDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			# Actualizar stock si es "recibida"
			if self.object.status == "recibida":
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date)
				self.object.apply_inventory_update()
				CashBox.register_purchase(self.object)

			messages.success(request, "Compra registrada exitosamente.")
			return redirect(self.success_url)
		else:
			return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = PurchaseDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = PurchaseDetailFormSet(instance=self.object)
		return super().get_context_data(**kwargs)


class PurchaseUpdateView(InventoryAccessMixin, UpdateView):
	model = Purchase
	form_class = PurchaseForm
	template_name = "compras/purchase_form.html"
	success_url = reverse_lazy("compras:list")

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if not self.object.is_editable():
			messages.warning(request, "Esta compra ya no puede editarse porque su estado no es Pendiente.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if not self.object.is_editable():
			messages.warning(request, "Esta compra ya no puede editarse porque su estado no es Pendiente.")
			return redirect(self.success_url)

		old_status = self.object.status

		form = self.get_form()
		formset = PurchaseDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			# Si cambió a "recibida" desde otro estado, actualizar stock
			if old_status != "recibida" and self.object.status == "recibida":
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date)
				self.object.apply_inventory_update()
				CashBox.register_purchase(self.object)
				messages.info(request, f"Stock actualizado: +{sum(d.quantity for d in self.object.purchasedetail_set.all())} unidades.")

			messages.success(request, "Compra actualizada exitosamente.")
			return redirect(self.success_url)
		else:
			return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = PurchaseDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = PurchaseDetailFormSet(instance=self.object)
		kwargs["purchase_locked"] = bool(self.object and not self.object.is_editable())
		return super().get_context_data(**kwargs)


class PurchaseDeleteView(InventoryAccessMixin, DeleteView):
	model = Purchase
	template_name = "compras/purchase_confirm_delete.html"
	success_url = reverse_lazy("compras:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status == "recibida":
			from caja.models import CashBox
			try:
				CashBox.validate_day_open()
				self.object.revert_inventory_update()
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			CashBox.register_purchase_reversal(self.object)
			messages.warning(request, "Compra eliminada y stock revertido.")
		else:
			messages.warning(request, "Compra eliminada.")
		return super().post(request, *args, **kwargs)
