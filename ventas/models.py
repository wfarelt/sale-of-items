from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class CommercialCondition(models.Model):
	CODE_CASH = "cash_0"
	CODE_CREDIT_7 = "credit_7"
	CODE_CREDIT_15 = "credit_15"
	CODE_CREDIT_30 = "credit_30"

	code = models.CharField(max_length=30, unique=True, verbose_name="Codigo")
	name = models.CharField(max_length=80, unique=True, verbose_name="Nombre")
	days_due = models.PositiveIntegerField(default=0, verbose_name="Dias de credito")
	is_cash_sale = models.BooleanField(default=False, verbose_name="Es contado")
	is_active = models.BooleanField(default=True, verbose_name="Activo")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["days_due", "name"]
		verbose_name = "Condicion comercial"
		verbose_name_plural = "Condiciones comerciales"

	def __str__(self):
		return self.name


class PaymentMethod(models.Model):
	CODE_CASH = "cash"
	CODE_QR = "qr"
	CODE_TRANSFER = "transferencia"
	CODE_CARD = "tarjeta"

	code = models.CharField(max_length=20, unique=True, verbose_name="Codigo")
	name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Medio de pago"
		verbose_name_plural = "Medios de pago"

	def __str__(self):
		return self.name


class Sale(models.Model):
	PAYMENT_TYPE_CHOICES = (
		("cash", "Efectivo"),
		("qr", "QR"),
		("transferencia", "Transferencia"),
		("tarjeta", "Tarjeta"),
	)

	STATUS_DRAFT = "draft"
	STATUS_RESERVED = "reserved"
	STATUS_ORDERED = "ordered"
	STATUS_CONFIRMED_FLOW = "confirmed"
	STATUS_DELIVERED_FLOW = "delivered"
	STATUS_CANCELLED_FLOW = "cancelled"

	STATUS_PROFORMA = "proforma"
	STATUS_CONFIRMED = "confirmada"
	STATUS_CANCELED = "anulada"
	STATUS_CHOICES = (
		(STATUS_DRAFT, "DRAFT - Proforma"),
		(STATUS_RESERVED, "RESERVED - Reserva"),
		(STATUS_ORDERED, "ORDERED - Pedido"),
		(STATUS_CONFIRMED_FLOW, "CONFIRMED - Venta aceptada"),
		(STATUS_DELIVERED_FLOW, "DELIVERED - Entregado"),
		(STATUS_CANCELLED_FLOW, "CANCELLED - Cancelado"),
		(STATUS_PROFORMA, "Proforma"),
		(STATUS_CONFIRMED, "Confirmada"),
		(STATUS_CANCELED, "Anulada"),
	)

	PAYMENT_STATUS_PENDING = "PENDING"
	PAYMENT_STATUS_PARTIAL = "PARTIAL"
	PAYMENT_STATUS_PAID = "PAID"

	date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
	client = models.ForeignKey("clientes.Client", on_delete=models.PROTECT, verbose_name="Cliente")
	commercial_condition = models.ForeignKey(
		CommercialCondition,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		verbose_name="Condicion comercial",
		related_name="sales",
	)
	seller = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		verbose_name="Vendedor",
		related_name="sales",
	)
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_CONFIRMED,
		verbose_name="Estado",
	)
	canceled_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		verbose_name="Anulada por",
		related_name="canceled_sales",
	)
	canceled_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de anulacion")
	delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de entrega")
	delivered_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		verbose_name="Entregada por",
		related_name="delivered_sales",
	)
	received_by_name = models.CharField(max_length=120, blank=True, verbose_name="Recibido por")
	received_by_doc = models.CharField(max_length=40, blank=True, verbose_name="Documento de quien recoge")
	delivery_notes = models.TextField(blank=True, verbose_name="Observaciones de entrega")
	due_date = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
	total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
	payment_type = models.CharField(
		max_length=20,
		choices=PAYMENT_TYPE_CHOICES,
		verbose_name="Tipo de pago (legacy)",
		null=True,
		blank=True,
	)
	backorder_purchase = models.ForeignKey(
		"compras.Purchase",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		verbose_name="Compra de respaldo (backorder)",
		related_name="backorder_sales",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		verbose_name = "Venta"
		verbose_name_plural = "Ventas"

	def __str__(self):
		return f"Venta #{self.pk} - {self.client.name}"

	def calculate_total(self):
		total = sum(detail.subtotal() for detail in self.saledetail_set.all())
		self.total = total
		self.save(update_fields=["total"])
		return total

	def calculate_due_date(self, *, save=True):
		if self.commercial_condition:
			self.due_date = (self.date or timezone.now()).date() + timedelta(days=self.commercial_condition.days_due)
		else:
			self.due_date = (self.date or timezone.now()).date()
		if save and self.pk:
			self.save(update_fields=["due_date", "updated_at"])
		return self.due_date

	@property
	def total_paid(self):
		if hasattr(self, "_prefetched_objects_cache") and "payments" in self._prefetched_objects_cache:
			return sum((payment.amount for payment in self._prefetched_objects_cache["payments"]), Decimal("0.00"))
		value = self.payments.aggregate(total=Sum("amount"))["total"]
		return value or Decimal("0.00")

	@property
	def pending_balance(self):
		balance = (self.total or Decimal("0.00")) - self.total_paid
		return balance if balance > 0 else Decimal("0.00")

	@property
	def payment_status(self):
		paid = self.total_paid
		total = self.total or Decimal("0.00")
		if paid <= Decimal("0.00"):
			return self.PAYMENT_STATUS_PENDING
		if paid < total:
			return self.PAYMENT_STATUS_PARTIAL
		return self.PAYMENT_STATUS_PAID

	def is_confirmed_state(self):
		return self.status in {self.STATUS_CONFIRMED, self.STATUS_CONFIRMED_FLOW}

	def is_canceled_state(self):
		return self.status in {self.STATUS_CANCELED, self.STATUS_CANCELLED_FLOW}

	def register_payment(self, *, method_code, amount, recorded_by=None, paid_at=None, reference="", notes=""):
		if amount is None or amount <= Decimal("0.00"):
			raise ValidationError("El monto del pago debe ser mayor a cero.")

		method = PaymentMethod.objects.filter(code=method_code, is_active=True).first()
		if not method:
			raise ValidationError("El medio de pago seleccionado no esta disponible.")

		payment = Payment.objects.create(
			sale=self,
			method=method,
			amount=amount,
			paid_at=paid_at or timezone.now(),
			recorded_by=recorded_by,
			reference=reference,
			notes=notes,
		)

		if not self.payment_type:
			self.payment_type = method.code
			self.save(update_fields=["payment_type", "updated_at"])

		return payment

	def apply_inventory_output(self):
		from movimientos.models import InventoryMovement

		for detail in self.saledetail_set.select_related("product"):
			if detail.product.stock < detail.quantity:
				raise ValidationError(f"Stock insuficiente para {detail.product.name}.")

		movement_details = []
		for detail in self.saledetail_set.select_related("product"):
			product = detail.product
			product.stock -= detail.quantity
			product.stock_reservado = max(product.stock_reservado - detail.quantity, 0)
			product.save(update_fields=["stock", "stock_reservado"])
			movement_details.append({"product": product, "quantity": detail.quantity})

		InventoryMovement.create_movement(
			movement_type=InventoryMovement.TYPE_OUT,
			reference=f"Venta #{self.pk}",
			description=f"Salida por venta al cliente {self.client.name}",
			details=movement_details,
		)

	def restore_inventory_output(self):
		from movimientos.models import InventoryMovement

		movement_details = []
		for detail in self.saledetail_set.select_related("product"):
			product = detail.product
			product.stock += detail.quantity
			product.save(update_fields=["stock"])
			movement_details.append({"product": product, "quantity": detail.quantity})

		InventoryMovement.create_movement(
			movement_type=InventoryMovement.TYPE_IN,
			reference=f"Anulación venta #{self.pk}",
			description=f"Reversa por anulación de venta al cliente {self.client.name}",
			details=movement_details,
		)

	def reserve_inventory(self):
		for detail in self.saledetail_set.select_related("product"):
			product = detail.product
			product.stock_reservado += detail.quantity
			product.save(update_fields=["stock_reservado"])

	def release_reservation(self):
		for detail in self.saledetail_set.select_related("product"):
			product = detail.product
			product.stock_reservado = max(product.stock_reservado - detail.quantity, 0)
			product.save(update_fields=["stock_reservado"])


class Payment(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments", verbose_name="Venta")
	method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name="payments", verbose_name="Medio de pago")
	amount = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		verbose_name="Monto",
		validators=[MinValueValidator(Decimal("0.01"))],
	)
	paid_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de pago")
	reference = models.CharField(max_length=80, blank=True, verbose_name="Referencia")
	notes = models.CharField(max_length=255, blank=True, verbose_name="Observaciones")
	recorded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="registered_payments",
		verbose_name="Registrado por",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-paid_at", "-id"]
		verbose_name = "Pago"
		verbose_name_plural = "Pagos"

	def __str__(self):
		return f"Pago #{self.pk} - Venta #{self.sale_id} - {self.amount}"


class SaleDetail(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name="Venta")
	product = models.ForeignKey("productos.Product", on_delete=models.PROTECT, verbose_name="Producto")
	quantity = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		verbose_name="Cantidad",
		validators=[MinValueValidator(Decimal("0.01"))],
	)
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
	discount = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		default=0,
		verbose_name="Descuento",
		validators=[MinValueValidator(Decimal("0.00"))],
	)
	ref_m2 = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		null=True,
		blank=True,
		verbose_name="Ref. m²",
	)
	cajas = models.PositiveIntegerField(
		null=True,
		blank=True,
		verbose_name="Cajas",
	)

	class Meta:
		ordering = ["sale"]
		verbose_name = "Detalle de venta"
		verbose_name_plural = "Detalles de venta"
		unique_together = ("sale", "product")

	def __str__(self):
		return f"{self.product.name} x {self.quantity}"

	def subtotal(self):
		gross = self.quantity * self.price
		net = gross - (self.discount or Decimal("0.00"))
		return net if net > 0 else Decimal("0.00")
