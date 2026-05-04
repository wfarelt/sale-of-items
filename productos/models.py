from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Categoria"
		verbose_name_plural = "Categorias"

	def __str__(self):
		return self.name


class Brand(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Marca"
		verbose_name_plural = "Marcas"

	def __str__(self):
		return self.name


class Formato(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Formato"
		verbose_name_plural = "Formatos"

	def __str__(self):
		return self.name


class Acabado(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Acabado"
		verbose_name_plural = "Acabados"

	def __str__(self):
		return self.name


class IndicacionesUso(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
	description = models.TextField(blank=True, verbose_name="Descripcion")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Indicaciones de uso"
		verbose_name_plural = "Indicaciones de uso"

	def __str__(self):
		return self.name


class M2Caja(models.Model):
	value = models.DecimalField(max_digits=7, decimal_places=2, unique=True, verbose_name="Valor (m²)")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["value"]
		verbose_name = "m² por caja"
		verbose_name_plural = "m² por caja"

	def __str__(self):
		return f"{self.value} m²"


class Product(models.Model):
	code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código")
	name = models.CharField(max_length=150, verbose_name="Nombre")
	description = models.TextField(blank=True, verbose_name="Descripcion")
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
	image = models.ImageField(upload_to="productos/", blank=True, null=True, verbose_name="Imagen")
	stock = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Stock")
	stock_reservado = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Stock reservado")
	stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock mínimo")
	color = models.CharField(max_length=50, blank=True, verbose_name="Color")
	brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Marca", null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
	formato = models.ForeignKey(Formato, on_delete=models.PROTECT, verbose_name="Formato", null=True, blank=True)
	acabado = models.ForeignKey(Acabado, on_delete=models.PROTECT, verbose_name="Acabado", null=True, blank=True)
	indicaciones_uso = models.ForeignKey(IndicacionesUso, on_delete=models.PROTECT, verbose_name="Indicaciones de uso", null=True, blank=True)
	metros_cuadrados_por_caja = models.ForeignKey(M2Caja, on_delete=models.PROTECT, verbose_name="m² por caja", null=True, blank=True)
	is_active = models.BooleanField(default=True, verbose_name="Activo")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Producto"
		verbose_name_plural = "Productos"

	def __str__(self):
		return self.name

	@property
	def available_stock(self):
		from decimal import Decimal
		available = self.stock - self.stock_reservado
		return available if available > Decimal("0") else Decimal("0")
