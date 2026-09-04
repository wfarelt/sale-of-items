from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import OperationalError, transaction
from decimal import Decimal
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from config.pdf_utils import render_to_pdf
from empresas.models import Company
from productos.models import Product
from .forms import SaleDeliveryForm, SaleDetailFormSet, SaleForm, SalePaymentForm
from .models import Sale


def _is_sqlite_locked_error(exc):
	return "database is locked" in str(exc).lower()


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
		queryset = super().get_queryset().select_related("client").prefetch_related("payments")
		if self.request.user.is_almacen:
			entrega = self.request.GET.get("entrega", "pendientes")
			if entrega == "entregadas":
				queryset = queryset.filter(
					delivered_at__isnull=False,
					status=Sale.STATUS_EXECUTED,
				)
			else:  # pendientes (default)
				queryset = queryset.filter(
					delivered_at__isnull=True,
					status=Sale.STATUS_EXECUTED,
				)
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(client__name__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		context["entrega_filter"] = self.request.GET.get("entrega", "pendientes")
		return context


class SaleDetailView(SalesAccessMixin, DetailView):
	model = Sale
	template_name = "ventas/sale_detail.html"
	context_object_name = "sale"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		details = list(self.object.saledetail_set.select_related("product"))
		payments = list(self.object.payments.select_related("method", "recorded_by"))
		context["details"] = details
		context["payments"] = payments
		context["payment_form"] = SalePaymentForm()
		context["total_discount"] = sum((detail.discount or Decimal("0.00")) for detail in details)
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
			try:
				new_status = form.cleaned_data.get("status")
				upfront_amount = form.cleaned_data.get("upfront_amount")
				self.object = form.save(commit=False)
				self.object.seller = request.user
				self.object.save()
				formset.instance = self.object
				formset.save()
				self.object.calculate_total()
				self.object.calculate_due_date()

				if upfront_amount is not None and upfront_amount > self.object.total:
					form.add_error("upfront_amount", "El pago inicial no puede superar el total de la venta.")
					self.object.delete()
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

				if new_status == Sale.STATUS_RESERVED:
					insufficient_stock = [
						detail.product.name
						for detail in self.object.saledetail_set.select_related("product")
						if detail.product.available_stock < detail.quantity
					]
					if insufficient_stock:
						form.add_error(None, "No se puede reservar: stock disponible insuficiente en " + ", ".join(insufficient_stock[:3]) + ".")
						self.object.delete()
						return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
					self.object.reserve_inventory()
					messages.success(request, "Venta guardada como RESERVA. Stock reservado actualizado.")
				elif new_status == Sale.STATUS_ORDERED:
					messages.success(request, "Venta guardada como IMPORTACIÓN.")
				elif new_status == Sale.STATUS_EXECUTED:
					from caja.models import CashBox

					CashBox.validate_day_open(self.object.date)
					self.object.apply_inventory_output()
					if upfront_amount is not None:
						payment = self.object.register_payment(
							method_code=form.cleaned_data["payment_type"],
							amount=upfront_amount,
							recorded_by=request.user,
							paid_at=self.object.date,
							notes="Pago inicial registrado al ejecutar la venta",
						)
						CashBox.register_sale_payment(payment)
					messages.success(request, "Venta ejecutada. Stock descontado.")
				else:
					messages.success(request, "Proforma guardada exitosamente.")

				return redirect(self.success_url)
			except OperationalError as exc:
				if _is_sqlite_locked_error(exc):
					message = "La base de datos está ocupada en este momento. Intenta guardar nuevamente en unos segundos."
					messages.error(request, message)
					form.add_error(None, message)
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				raise

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
				"stock_reservado": float(product.stock_reservado),
				"available_stock": float(product.available_stock),
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
			try:
				new_status = form.cleaned_data.get("status")
				upfront_amount = form.cleaned_data.get("upfront_amount")
				if new_status == Sale.STATUS_RESERVED:
					insufficient_stock = [
						form_detail.cleaned_data["product"].name
						for form_detail in formset.forms
						if not form_detail.cleaned_data.get("DELETE")
						and form_detail.cleaned_data.get("product")
						and form_detail.cleaned_data["product"].available_stock < form_detail.cleaned_data["quantity"]
					]
					if insufficient_stock:
						form.add_error(None, "No se puede reservar: stock disponible insuficiente en " + ", ".join(insufficient_stock[:3]) + ".")
						return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				self.object = form.save(commit=False)
				self.object.save()
				formset.instance = self.object
				formset.save()
				self.object.calculate_total()
				self.object.calculate_due_date()

				if upfront_amount is not None and upfront_amount > self.object.total:
					form.add_error("upfront_amount", "El pago inicial no puede superar el total de la venta.")
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

				if new_status == Sale.STATUS_RESERVED:
					self.object.reserve_inventory()
					messages.success(request, "Venta guardada como RESERVA. Stock reservado actualizado.")
				elif new_status == Sale.STATUS_ORDERED:
					messages.success(request, "Venta guardada como IMPORTACIÓN.")
				elif new_status == Sale.STATUS_EXECUTED:
					from caja.models import CashBox

					CashBox.validate_day_open(self.object.date)
					self.object.apply_inventory_output()
					if upfront_amount is not None:
						payment = self.object.register_payment(
							method_code=form.cleaned_data["payment_type"],
							amount=upfront_amount,
							recorded_by=request.user,
							paid_at=self.object.date,
							notes="Pago inicial registrado al ejecutar la venta",
						)
						CashBox.register_sale_payment(payment)
					messages.success(request, "Venta ejecutada. Stock descontado.")
				else:
					messages.success(request, "Proforma actualizada exitosamente.")

				return redirect(self.success_url)
			except OperationalError as exc:
				if _is_sqlite_locked_error(exc):
					message = "La base de datos está ocupada en este momento. Intenta guardar nuevamente en unos segundos."
					messages.error(request, message)
					form.add_error(None, message)
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				raise

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
				"stock_reservado": float(product.stock_reservado),
				"available_stock": float(product.available_stock),
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
		if self.object.is_canceled_state():
			messages.info(request, "La venta ya se encuentra anulada.")
			return redirect(self.success_url)

		if not self.object.is_executed_state():
			messages.error(request, "Solo se pueden anular ventas ejecutadas.")
			return redirect(self.success_url)

		if self.object.is_executed_state():
			from caja.models import CashBox
			try:
				CashBox.validate_day_open()
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			self.object.restore_inventory_output()
			payments = list(self.object.payments.select_related("method"))
			if payments:
				for payment in payments:
					CashBox.register_sale_payment_reversal(payment)
			else:
				CashBox.register_sale_reversal(self.object)
			messages.warning(request, "Venta anulada y stock restaurado.")
		self.object.status = self.object.STATUS_CANCELLED
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
		if self.object.is_canceled_state():
			messages.error(request, "No puedes registrar entrega en una venta anulada.")
			return redirect("ventas:detail", pk=self.object.pk)
		if not self.object.is_executed_state():
			messages.error(request, "Solo puedes registrar entrega en ventas ejecutadas.")
			return redirect("ventas:detail", pk=self.object.pk)
		if self.object.delivery_status == Sale.DELIVERY_STATUS_DELIVERED:
			messages.info(request, "La venta ya se encuentra entregada.")
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
			"received_by_name", "received_by_doc", "delivery_notes", "delivered_at", "delivered_by", "updated_at",
		])
		messages.success(self.request, "Entrega registrada exitosamente.")
		return redirect(self.get_success_url())


class SalePDFView(SalesAccessMixin, View):
	def get(self, request, pk, *args, **kwargs):
		sale = Sale.objects.select_related("client", "seller", "delivered_by", "commercial_condition").get(pk=pk)
		details = list(sale.saledetail_set.select_related("product").all())
		payments = list(sale.payments.select_related("method").all())
		total_discount = sum((detail.discount or Decimal("0.00")) for detail in details)
		current_user_name = request.user.get_full_name() or request.user.username
		context = {
			"sale": sale,
			"details": details,
			"payments": payments,
			"total_discount": total_discount,
			"company": Company.get_solo(),
			"now": timezone.localtime(),
			"show_prices": not request.user.is_almacen,
			"is_almacen_user": request.user.is_almacen,
			"current_user_name": current_user_name,
		}
		year = timezone.localtime().year
		sale_number = f"{year}{sale.id:03d}"
		client_name = sale.client.name.upper() if getattr(sale, 'client', None) and sale.client.name else "CLIENTE"
		# Remove characters not allowed in Windows filenames
		for ch in '\\/:*?"<>|':
			client_name = client_name.replace(ch, '')
		client_name = client_name.strip()
		suffix = " (ENTREGA)" if request.user.is_almacen else ""
		filename = f"{sale_number} - {client_name}{suffix}.pdf"
		return render_to_pdf("ventas/sale_pdf.html", context, filename=filename, base_url=request.build_absolute_uri("/"))


class SaleRegisterPaymentView(SalesWriteAccessMixin, View):
	@transaction.atomic
	def post(self, request, pk, *args, **kwargs):
		sale = Sale.objects.select_related("client").get(pk=pk)
		if sale.is_canceled_state():
			messages.error(request, "No puedes registrar pagos para una venta anulada.")
			return redirect("ventas:detail", pk=sale.pk)
		if not sale.is_executed_state():
			messages.error(request, "Solo puedes registrar pagos para una venta ejecutada.")
			return redirect("ventas:detail", pk=sale.pk)

		form = SalePaymentForm(request.POST)
		if not form.is_valid():
			messages.error(request, "No se pudo registrar el pago. Verifica los datos ingresados.")
			return redirect("ventas:detail", pk=sale.pk)

		method = form.cleaned_data["method"]
		amount = form.cleaned_data["amount"]
		reference = form.cleaned_data.get("reference", "")
		notes = form.cleaned_data.get("notes", "")

		if amount > sale.pending_balance:
			messages.error(request, "El pago no puede superar el saldo pendiente.")
			return redirect("ventas:detail", pk=sale.pk)

		from caja.models import CashBox
		try:
			CashBox.validate_day_open(timezone.now())
			payment = sale.register_payment(
				method_code=method.code,
				amount=amount,
				recorded_by=request.user,
				reference=reference,
				notes=notes,
			)
			CashBox.register_sale_payment(payment)
		except ValidationError as exc:
			messages.error(request, str(exc))
			return redirect("ventas:detail", pk=sale.pk)

		messages.success(request, "Pago registrado exitosamente.")
		return redirect("ventas:detail", pk=sale.pk)


class SaleCreatePurchaseView(SalesWriteAccessMixin, View):
	"""Creates a Purchase pre-populated from an ORDERED Sale and links them."""

	@transaction.atomic
	def post(self, request, pk, *args, **kwargs):
		from compras.models import Purchase, PurchaseDetail

		sale = Sale.objects.select_related("client").prefetch_related(
			"saledetail_set__product"
		).get(pk=pk)

		if sale.status != Sale.STATUS_ORDERED:
			messages.error(request, "Solo se puede generar una compra desde ventas en estado ORDERED.")
			return redirect("ventas:detail", pk=sale.pk)

		if sale.backorder_purchase_id:
			messages.warning(request, "Esta venta ya tiene una compra de respaldo vinculada.")
			return redirect("ventas:detail", pk=sale.pk)

		purchase = Purchase.objects.create(status="pendiente")

		for detail in sale.saledetail_set.all():
			PurchaseDetail.objects.create(
				purchase=purchase,
				product=detail.product,
				quantity=detail.quantity,
				cost_price=detail.product.price,
			)

		purchase.calculate_total()
		sale.backorder_purchase = purchase
		sale.save(update_fields=["backorder_purchase", "updated_at"])

		messages.success(
			request,
			f"Compra #{purchase.pk} creada como respaldo del pedido. Completa el proveedor y ajusta si es necesario.",
		)
		return redirect("compras:update", pk=purchase.pk)


class SaleStatusTransitionView(SalesAccessMixin, View):
	"""Handles status transitions for the new fulfillment flow:
	reserve, order, execute, revert, cancel.
	"""

	ALLOWED_ROLES_PER_ACTION = {
		"reserve": ("is_admin", "is_vendedor"),
		"order": ("is_admin", "is_vendedor"),
		"execute": ("is_admin", "is_vendedor"),
		"revert": ("is_admin", "is_vendedor"),
		"cancel": ("is_admin",),
	}

	def test_func(self):
		return (
			self.request.user.is_admin
			or self.request.user.is_vendedor
			or self.request.user.is_almacen
		)

	@transaction.atomic
	def post(self, request, pk, *args, **kwargs):
		sale = Sale.objects.select_related("client", "commercial_condition").get(pk=pk)
		action = request.POST.get("action", "")
		allowed_roles = self.ALLOWED_ROLES_PER_ACTION.get(action, ())
		if not any(getattr(request.user, role, False) for role in allowed_roles):
			messages.error(request, "No tienes permiso para realizar esta acción.")
			return redirect("ventas:detail", pk=sale.pk)

		if action == "reserve":
			allowed_from = {Sale.STATUS_PROFORMA}
			if sale.status not in allowed_from:
				messages.error(request, "Solo se puede reservar desde estado proforma.")
				return redirect("ventas:detail", pk=sale.pk)
			sale.reserve_inventory()
			sale.status = Sale.STATUS_RESERVED
			sale.save(update_fields=["status", "updated_at"])
			messages.success(request, "Venta marcada como RESERVADA. Stock reservado actualizado.")

		elif action == "order":
			allowed_from = {Sale.STATUS_PROFORMA}
			if sale.status not in allowed_from:
				messages.error(request, "Solo se puede registrar como pedido desde estado proforma.")
				return redirect("ventas:detail", pk=sale.pk)
			sale.status = Sale.STATUS_ORDERED
			sale.save(update_fields=["status", "updated_at"])
			messages.success(request, "Venta marcada como PEDIDO. Sin impacto en inventario hasta la entrega.")

		elif action == "execute":
			allowed_from = {Sale.STATUS_PROFORMA, Sale.STATUS_RESERVED, Sale.STATUS_ORDERED}
			if sale.status == Sale.STATUS_EXECUTED:
				messages.info(request, "La venta ya está ejecutada.")
				return redirect("ventas:detail", pk=sale.pk)
			if sale.status not in allowed_from:
				messages.error(request, "Solo se puede ejecutar desde proforma, reserva o importación.")
				return redirect("ventas:detail", pk=sale.pk)
			if sale.status == Sale.STATUS_RESERVED:
				insufficient_stock = []
				for detail in sale.saledetail_set.select_related("product"):
					in_stock = detail.product.stock
					if in_stock < detail.quantity:
						insufficient_stock.append(
							f"{detail.product.name} (stock: {in_stock}, req: {detail.quantity})"
						)
				if insufficient_stock:
					messages.error(
						request,
						"No se puede ejecutar desde reserva: stock insuficiente en " + ", ".join(insufficient_stock[:3])
						+ ("." if len(insufficient_stock) <= 3 else ", ..."),
					)
					return redirect("ventas:detail", pk=sale.pk)

				missing_reservation = []
				for detail in sale.saledetail_set.select_related("product"):
					reserved = detail.product.stock_reservado
					if reserved < detail.quantity:
						missing_reservation.append(
							f"{detail.product.name} (reservado: {reserved}, req: {detail.quantity})"
						)
				if missing_reservation:
					messages.error(
						request,
						"No se puede ejecutar: la reserva no cubre la venta en " + ", ".join(missing_reservation[:3])
						+ ("." if len(missing_reservation) <= 3 else ", ..."),
					)
					return redirect("ventas:detail", pk=sale.pk)
			if sale.status in {Sale.STATUS_PROFORMA, Sale.STATUS_ORDERED}:
				insufficient_stock = []
				for detail in sale.saledetail_set.select_related("product"):
					available = detail.product.available_stock
					if available < detail.quantity:
						insufficient_stock.append(
							f"{detail.product.name} (disp: {available}, req: {detail.quantity})"
						)
				if insufficient_stock:
					messages.error(
						request,
						"No se puede ejecutar: stock insuficiente en " + ", ".join(insufficient_stock[:3])
						+ ("." if len(insufficient_stock) <= 3 else ", ..."),
					)
					return redirect("ventas:detail", pk=sale.pk)
			sale.apply_inventory_output()
			sale.status = Sale.STATUS_EXECUTED
			sale.save(update_fields=["status", "updated_at"])
			messages.success(request, "Venta EJECUTADA. Stock descontado.")

		elif action == "revert":
			if sale.status not in {Sale.STATUS_RESERVED, Sale.STATUS_ORDERED}:
				messages.error(request, "Solo una reserva o importación puede volver a proforma.")
				return redirect("ventas:detail", pk=sale.pk)
			if sale.status == Sale.STATUS_RESERVED:
				sale.release_reservation()
			sale.status = Sale.STATUS_PROFORMA
			sale.save(update_fields=["status", "updated_at"])
			messages.success(request, "Venta devuelta a PROFORMA.")

		elif action == "cancel":
			if sale.status != Sale.STATUS_EXECUTED:
				messages.error(request, "Solo una venta ejecutada puede anularse.")
				return redirect("ventas:detail", pk=sale.pk)
			sale.restore_inventory_output()
			payments = list(sale.payments.select_related("method"))
			if payments:
				from caja.models import CashBox

				CashBox.validate_day_open(timezone.now())
				for payment in payments:
					CashBox.register_sale_payment_reversal(payment)
			sale.status = Sale.STATUS_CANCELLED
			sale.canceled_by = request.user
			sale.canceled_at = timezone.now()
			sale.save(update_fields=["status", "canceled_by", "canceled_at", "updated_at"])
			messages.warning(request, "Venta cancelada.")

		else:
			messages.error(request, "Acción no reconocida.")

		return redirect("ventas:detail", pk=sale.pk)


class SaleAgingReportView(SalesWriteAccessMixin, View):
	"""Accounts-receivable aging report: sales with pending balance grouped by overdue bucket."""

	def get(self, request, *args, **kwargs):
		today = timezone.localdate()
		allowed_statuses = {
			Sale.STATUS_RESERVED,
			Sale.STATUS_ORDERED,
			Sale.STATUS_EXECUTED,
		}

		sales = (
			Sale.objects
			.filter(status__in=allowed_statuses)
			.filter(total__gt=0)
			.select_related("client", "commercial_condition", "seller")
			.prefetch_related("payments")
			.order_by("due_date", "-date")
		)

		buckets = {
			"current": {"label": "Vigente", "color": "success", "sales": [], "total": Decimal("0.00")},
			"1_30":    {"label": "1–30 días", "color": "warning", "sales": [], "total": Decimal("0.00")},
			"31_60":   {"label": "31–60 días", "color": "orange", "sales": [], "total": Decimal("0.00")},
			"61_90":   {"label": "61–90 días", "color": "danger", "sales": [], "total": Decimal("0.00")},
			"91_plus": {"label": "+90 días", "color": "dark", "sales": [], "total": Decimal("0.00")},
		}

		grand_total = Decimal("0.00")
		grand_count = 0

		for sale in sales:
			pending = sale.pending_balance
			if pending <= Decimal("0.00"):
				continue

			days_overdue = (today - sale.due_date).days if sale.due_date else 0
			sale.days_overdue = days_overdue
			sale.balance_due = pending

			if days_overdue <= 0:
				key = "current"
			elif days_overdue <= 30:
				key = "1_30"
			elif days_overdue <= 60:
				key = "31_60"
			elif days_overdue <= 90:
				key = "61_90"
			else:
				key = "91_plus"

			buckets[key]["sales"].append(sale)
			buckets[key]["total"] += pending
			grand_total += pending
			grand_count += 1

		return render(request, "ventas/sale_aging_report.html", {
			"buckets": buckets,
			"grand_total": grand_total,
			"grand_count": grand_count,
			"today": today,
		})
