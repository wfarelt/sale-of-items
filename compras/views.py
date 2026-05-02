from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PurchaseDetailFormSet, PurchaseForm
from .models import Purchase


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class PurchaseListView(InventoryAccessMixin, ListView):
	model = Purchase
	template_name = "compras/purchase_list.html"
	context_object_name = "purchases"
	paginate_by = 20

	def get_queryset(self):
		queryset = Purchase.objects.select_related("supplier")
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(
				Q(supplier__nombre__icontains=search) | Q(invoice_number__icontains=search)
			)
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

			if self.object.status == "recibida":
				self.object.apply_inventory_update()

			messages.success(request, "Compra registrada exitosamente.")
			return redirect(self.success_url)

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

			if old_status != "recibida" and self.object.status == "recibida":
				self.object.apply_inventory_update()
				messages.info(request, f"Stock actualizado: +{sum(d.quantity for d in self.object.purchasedetail_set.all())} unidades.")

			messages.success(request, "Compra actualizada exitosamente.")
			return redirect(self.success_url)

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
			try:
				self.object.revert_inventory_update()
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			messages.warning(request, "Compra eliminada y stock revertido.")
		else:
			messages.warning(request, "Compra eliminada.")
		return super().post(request, *args, **kwargs)
