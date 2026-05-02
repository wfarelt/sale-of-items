from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models


class Purchase(models.Model):
	STATUS_CHOICES = (
		("pendiente", "Pendiente"),
		("recibida", "Recibida"),
		("cancelada", "Cancelada"),
	)

	date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
	supplier = models.ForeignKey(
		"proveedores.Proveedor",
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		verbose_name="Proveedor",
	)
	invoice_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Numero de factura")
	total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendiente", verbose_name="Estado")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		verbose_name = "Compra"
		verbose_name_plural = "Compras"

	def __str__(self):
		supplier_name = self.supplier.nombre if self.supplier else "Sin proveedor"
		return f"Compra #{self.pk} - {supplier_name} - {self.date.strftime('%d/%m/%Y')}"

	def calculate_total(self):
		"""Calcula el total basado en los detalles de la compra"""
		total = sum(
			detail.quantity * detail.cost_price
			for detail in self.purchasedetail_set.all()
		)
		self.total = total
		self.save(update_fields=["total"])
		return total

	def is_editable(self):
		return self.status == "pendiente"

	def apply_inventory_update(self):
		"""Aplica incremento de stock y actualiza precio de venta en productos."""
		from movimientos.models import InventoryMovement

		movement_details = []
		for detail in self.purchasedetail_set.select_related("product"):
			product = detail.product
			sale_price = detail.sale_price if detail.sale_price is not None else detail.cost_price * 1.35
			product.stock += detail.quantity
			product.price = sale_price
			product.save(update_fields=["stock", "price"])
			movement_details.append({"product": product, "quantity": detail.quantity})

		InventoryMovement.create_movement(
			movement_type=InventoryMovement.TYPE_IN,
			reference=f"Compra #{self.pk}",
			description=f"Ingreso por compra al proveedor {self.supplier or 'Sin proveedor'}",
			details=movement_details,
		)

	def revert_inventory_update(self):
		from movimientos.models import InventoryMovement

		for detail in self.purchasedetail_set.select_related("product"):
			if detail.product.stock < detail.quantity:
				raise ValidationError(
					f"No se puede revertir la compra porque el producto {detail.product.name} ya no tiene stock suficiente."
				)

		movement_details = []
		for detail in self.purchasedetail_set.select_related("product"):
			product = detail.product
			product.stock -= detail.quantity
			product.save(update_fields=["stock"])
			movement_details.append({"product": product, "quantity": detail.quantity})

		InventoryMovement.create_movement(
			movement_type=InventoryMovement.TYPE_OUT,
			reference=f"Eliminación compra #{self.pk}",
			description=f"Reversa de compra del proveedor {self.supplier or 'Sin proveedor'}",
			details=movement_details,
		)


class PurchaseDetail(models.Model):
	purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, verbose_name="Compra")
	product = models.ForeignKey('productos.Product', on_delete=models.PROTECT, verbose_name="Producto")
	quantity = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		verbose_name="Cantidad",
		validators=[MinValueValidator(Decimal("0.01"))],
	)
	cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
	sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio de venta")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["purchase"]
		verbose_name = "Detalle de compra"
		verbose_name_plural = "Detalles de compra"
		unique_together = ("purchase", "product")

	def __str__(self):
		return f"{self.product.name} x {self.quantity} - Compra #{self.purchase.pk}"

	def subtotal(self):
		return self.quantity * self.cost_price
