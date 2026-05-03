from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from config.pdf_utils import render_to_pdf
from empresas.models import Company
from productos.models import Product
from .forms import SaleDeliveryForm, SaleDetailFormSet, SaleForm
from .models import Sale


class SalesAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_vendedor or self.request.user.is_almacen


class SalesWriteAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_vendedor


class SalesDeliveryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class SaleListView(SalesAccessMixin, ListView):
	model = Sale
	template_name = "ventas/sale_list.html"
	context_object_name = "sales"
	paginate_by = 20

	def get_queryset(self):
		queryset = super().get_queryset().select_related("client")
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(client__name__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		return context


class SaleDetailView(SalesAccessMixin, DetailView):
	model = Sale
	template_name = "ventas/sale_detail.html"
	context_object_name = "sale"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["details"] = self.object.saledetail_set.select_related("product")
		return context


class SaleCreateView(SalesWriteAccessMixin, CreateView):
	model = Sale
	form_class = SaleForm
	template_name = "ventas/sale_form.html"
	success_url = reverse_lazy("ventas:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = SaleDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			new_status = form.cleaned_data.get("status")
			if new_status == Sale.STATUS_CONFIRMED:
				from caja.models import CashBox
				try:
					CashBox.validate_day_open(timezone.now())
				except ValidationError as exc:
					messages.error(request, str(exc))
					form.add_error(None, str(exc))
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

			self.object = form.save(commit=False)
			self.object.seller = request.user
			self.object.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			if self.object.status == self.object.STATUS_CONFIRMED:
				from caja.models import CashBox
				try:
					CashBox.validate_day_open(self.object.date)
					self.object.apply_inventory_output()
					CashBox.register_sale(self.object)
				except ValidationError as exc:
					messages.error(request, str(exc))
					form.add_error(None, str(exc))
					self.object.delete()
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				messages.success(request, "Venta registrada exitosamente.")
			else:
				messages.success(request, "Proforma guardada exitosamente.")

			return redirect(self.success_url)

		return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = SaleDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = SaleDetailFormSet(instance=self.object)
		products_qs = Product.objects.select_related(
			"brand", "category", "formato", "acabado", "indicaciones_uso", "metros_cuadrados_por_caja"
		).filter(is_active=True)
		kwargs["products_data"] = [
			{
				"id": product.id,
				"code": product.code or "",
				"name": product.name,
				"price": float(product.price),
				"stock": float(product.stock),
				"brand": product.brand.name if product.brand else "",
				"category": product.category.name,
				"color": product.color,
				"formato": product.formato.name if product.formato else "",
				"acabado": product.acabado.name if product.acabado else "",
				"indicaciones_uso": product.indicaciones_uso.name if product.indicaciones_uso else "",
				"m2_por_caja": float(product.metros_cuadrados_por_caja.value) if product.metros_cuadrados_por_caja else None,
				"image": product.image.url if product.image else "",
			}
			for product in products_qs
		]
		return super().get_context_data(**kwargs)


class SaleUpdateView(SalesWriteAccessMixin, UpdateView):
	model = Sale
	form_class = SaleForm
	template_name = "ventas/sale_form.html"
	success_url = reverse_lazy("ventas:list")

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status != Sale.STATUS_PROFORMA:
			messages.error(request, "Solo se pueden editar ventas en estado proforma.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status != Sale.STATUS_PROFORMA:
			messages.error(request, "Solo se pueden editar ventas en estado proforma.")
			return redirect(self.success_url)

		form = self.get_form()
		formset = SaleDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			new_status = form.cleaned_data.get("status")
			if new_status == Sale.STATUS_CONFIRMED:
				from caja.models import CashBox
				try:
					CashBox.validate_day_open(self.object.date)
				except ValidationError as exc:
					messages.error(request, str(exc))
					form.add_error(None, str(exc))
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

			self.object = form.save(commit=False)
			self.object.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			if new_status == Sale.STATUS_CONFIRMED:
				from caja.models import CashBox
				try:
					self.object.apply_inventory_output()
					CashBox.register_sale(self.object)
				except ValidationError as exc:
					messages.error(request, str(exc))
					form.add_error(None, str(exc))
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				messages.success(request, "Proforma confirmada como venta exitosamente.")
			else:
				messages.success(request, "Proforma actualizada exitosamente.")

			return redirect(self.success_url)

		return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = SaleDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = SaleDetailFormSet(instance=self.object)
		products_qs = Product.objects.select_related(
			"brand", "category", "formato", "acabado", "indicaciones_uso", "metros_cuadrados_por_caja"
		).filter(is_active=True)
		kwargs["products_data"] = [
			{
				"id": product.id,
				"code": product.code or "",
				"name": product.name,
				"price": float(product.price),
				"stock": float(product.stock),
				"brand": product.brand.name if product.brand else "",
				"category": product.category.name,
				"color": product.color,
				"formato": product.formato.name if product.formato else "",
				"acabado": product.acabado.name if product.acabado else "",
				"indicaciones_uso": product.indicaciones_uso.name if product.indicaciones_uso else "",
				"m2_por_caja": float(product.metros_cuadrados_por_caja.value) if product.metros_cuadrados_por_caja else None,
				"image": product.image.url if product.image else "",
			}
			for product in products_qs
		]
		kwargs["is_edit"] = True
		return super().get_context_data(**kwargs)


class SaleDeleteView(SalesAccessMixin, DeleteView):
	model = Sale
	template_name = "ventas/sale_confirm_delete.html"
	success_url = reverse_lazy("ventas:list")

	def get(self, request, *args, **kwargs):
		if not request.user.is_admin:
			messages.error(request, "Solo un administrador puede anular ventas.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		if not request.user.is_admin:
			messages.error(request, "Solo un administrador puede anular ventas.")
			return redirect(self.success_url)

		self.object = self.get_object()
		if self.object.status == self.object.STATUS_CANCELED:
			messages.info(request, "La venta ya se encuentra anulada.")
			return redirect(self.success_url)

		if self.object.status == self.object.STATUS_CONFIRMED:
			from caja.models import CashBox
			try:
				CashBox.validate_day_open()
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			self.object.restore_inventory_output()
			CashBox.register_sale_reversal(self.object)
			messages.warning(request, "Venta anulada y stock restaurado.")
		else:
			messages.warning(request, "Proforma anulada.")

		self.object.status = self.object.STATUS_CANCELED
		self.object.canceled_by = request.user
		self.object.canceled_at = timezone.now()
		self.object.save(update_fields=["status", "canceled_by", "canceled_at", "updated_at"])
		return redirect(self.success_url)


class SaleDeliveryView(SalesDeliveryAccessMixin, UpdateView):
	model = Sale
	form_class = SaleDeliveryForm
	template_name = "ventas/sale_delivery_form.html"

	def get_success_url(self):
		return reverse_lazy("ventas:detail", kwargs={"pk": self.object.pk})

	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status == Sale.STATUS_CANCELED:
			messages.error(request, "No puedes registrar entrega en una venta anulada.")
			return redirect("ventas:detail", pk=self.object.pk)
		if self.object.status != Sale.STATUS_CONFIRMED:
			messages.error(request, "Solo puedes registrar entrega en ventas confirmadas.")
			return redirect("ventas:detail", pk=self.object.pk)
		return super().dispatch(request, *args, **kwargs)

	def get_initial(self):
		initial = super().get_initial()
		if self.object.received_by_name:
			initial["received_by_name"] = self.object.received_by_name
		if self.object.received_by_doc:
			initial["received_by_doc"] = self.object.received_by_doc
		if self.object.delivery_notes:
			initial["delivery_notes"] = self.object.delivery_notes
		return initial

	@transaction.atomic
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.delivered_at = timezone.now()
		self.object.delivered_by = self.request.user
		self.object.save(update_fields=[
			"received_by_name",
			"received_by_doc",
			"delivery_notes",
			"delivered_at",
			"delivered_by",
			"updated_at",
		])
		messages.success(self.request, "Entrega registrada exitosamente.")
		return redirect(self.get_success_url())


class SalePDFView(SalesAccessMixin, View):
	def get(self, request, pk, *args, **kwargs):
		sale = Sale.objects.select_related("client", "seller", "delivered_by").get(pk=pk)
		details = sale.saledetail_set.select_related("product").all()
		context = {
			"sale": sale,
			"details": details,
			"company": Company.get_solo(),
			"now": timezone.localtime(),
			"show_prices": not request.user.is_almacen,
		}
		filename = f"venta_{sale.id}.pdf"
		return render_to_pdf("ventas/sale_pdf.html", context, filename=filename, base_url=request.build_absolute_uri("/"))
