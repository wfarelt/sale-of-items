from django.db import models


class Category(models.Model):
	company = models.ForeignKey(
		'empresas.Company',
		on_delete=models.CASCADE,
		verbose_name='Empresa',
		related_name='categories',
	)
	name = models.CharField(max_length=100, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Categoria"
		verbose_name_plural = "Categorias"
		unique_together = [('company', 'name')]

	def __str__(self):
		return self.name


class Brand(models.Model):
	company = models.ForeignKey(
		'empresas.Company',
		on_delete=models.CASCADE,
		verbose_name='Empresa',
		related_name='brands',
	)
	name = models.CharField(max_length=100, verbose_name="Nombre")
	is_active = models.BooleanField(default=True, verbose_name="Activo")

	class Meta:
		ordering = ["name"]
		verbose_name = "Marca"
		verbose_name_plural = "Marcas"
		unique_together = [('company', 'name')]

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

	company = models.ForeignKey(
		'empresas.Company',
		on_delete=models.CASCADE,
		verbose_name='Empresa',
		related_name='products',
	)
	code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código")
	name = models.CharField(max_length=150, verbose_name="Nombre")
	description = models.TextField(blank=True, verbose_name="Descripcion")
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
	image = models.ImageField(upload_to="productos/", blank=True, null=True, verbose_name="Imagen")
	stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
	size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, verbose_name="Talla")
	color = models.CharField(max_length=50, blank=True, verbose_name="Color")
	brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Marca")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoria")
	is_active = models.BooleanField(default=True, verbose_name="Activo")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Producto"
		verbose_name_plural = "Productos"
		unique_together = [('company', 'code')]

	def __str__(self):
		return self.name

