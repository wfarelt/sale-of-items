from django.db import models

from productos.models import Product


class InventoryMovement(models.Model):
	TYPE_IN = "IN"
	TYPE_OUT = "OUT"
	TYPE_CHOICES = (
		(TYPE_IN, "Entrada"),
		(TYPE_OUT, "Salida"),
	)

	# Legacy fields kept nullable for backward compatibility with previous records.
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="legacy_movements", verbose_name="Producto", null=True, blank=True)
	type = models.CharField(max_length=3, choices=TYPE_CHOICES, verbose_name="Tipo")
	quantity = models.PositiveIntegerField(verbose_name="Cantidad", null=True, blank=True)
	date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
	reference = models.CharField(max_length=120, verbose_name="Referencia")
	description = models.TextField(blank=True, verbose_name="Descripción")

	class Meta:
		ordering = ["-date", "-id"]
		verbose_name = "Movimiento de inventario"
		verbose_name_plural = "Movimientos de inventario"

	def __str__(self):
		return f"{self.get_type_display()} - {self.reference}"

	def total_quantity(self):
		detail_total = self.details.aggregate(total=models.Sum("quantity"))["total"]
		if detail_total is not None:
			return detail_total
		return self.quantity or 0

	@classmethod
	def create_movement(cls, movement_type, reference, description="", details=None):
		movement = cls.objects.create(
			type=movement_type,
			reference=reference,
			description=description,
		)

		if details:
			for item in details:
				InventoryMovementDetail.objects.create(
					movement=movement,
					product=item["product"],
					quantity=item["quantity"],
				)

		return movement


class InventoryMovementDetail(models.Model):
	movement = models.ForeignKey(InventoryMovement, on_delete=models.CASCADE, related_name="details", verbose_name="Movimiento")
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movement_details", verbose_name="Producto")
	quantity = models.PositiveIntegerField(verbose_name="Cantidad")

	class Meta:
		verbose_name = "Detalle de movimiento"
		verbose_name_plural = "Detalles de movimiento"

	def __str__(self):
		return f"{self.product.name} x {self.quantity}"
