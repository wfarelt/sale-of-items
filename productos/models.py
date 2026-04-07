from django.db import models


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")

	class Meta:
		ordering = ["name"]
		verbose_name = "Categoria"
		verbose_name_plural = "Categorias"

	def __str__(self):
		return self.name


class Brand(models.Model):
	name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")

	class Meta:
		ordering = ["name"]
		verbose_name = "Marca"
		verbose_name_plural = "Marcas"

	def __str__(self):
		return self.name


class Product(models.Model):
	SIZE_CHOICES = (
		("XS", "XS"),
		("S", "S"),
		("M", "M"),
		("L", "L"),
		("XL", "XL"),
		("XXL", "XXL"),
	)

	code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Código")
	name = models.CharField(max_length=150, verbose_name="Nombre")
	description = models.TextField(blank=True, verbose_name="Descripcion")
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
	image = models.ImageField(upload_to="productos/", blank=True, null=True, verbose_name="Imagen")
	stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
	size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, verbose_name="Talla")
	color = models.CharField(max_length=50, blank=True, verbose_name="Color")
	brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Marca")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Producto"
		verbose_name_plural = "Productos"

	def __str__(self):
		return self.name
