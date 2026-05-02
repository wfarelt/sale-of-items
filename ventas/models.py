from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Sale(models.Model):
	PAYMENT_TYPE_CHOICES = (
		("cash", "Efectivo"),
		("qr", "QR"),
		("transferencia", "Transferencia"),
	)

	STATUS_PROFORMA = "proforma"
	STATUS_CONFIRMED = "confirmada"
	STATUS_CANCELED = "anulada"
	STATUS_CHOICES = (
		(STATUS_PROFORMA, "Proforma"),
		(STATUS_CONFIRMED, "Confirmada"),
		(STATUS_CANCELED, "Anulada"),
	)

	date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
	client = models.ForeignKey("clientes.Client", on_delete=models.PROTECT, verbose_name="Cliente")
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
	total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
	payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name="Tipo de pago")
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

	def apply_inventory_output(self):
		from movimientos.models import InventoryMovement

		for detail in self.saledetail_set.select_related("product"):
			if detail.product.stock < detail.quantity:
				raise ValidationError(f"Stock insuficiente para {detail.product.name}.")

		movement_details = []
		for detail in self.saledetail_set.select_related("product"):
			product = detail.product
			product.stock -= detail.quantity
			product.save(update_fields=["stock"])
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
