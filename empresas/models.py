from django.db import models


class Company(models.Model):
	name = models.CharField(max_length=200, unique=True, verbose_name='Nombre')
	ruc_nit = models.CharField(max_length=30, blank=True, verbose_name='RUC/NIT')
	email = models.EmailField(blank=True, verbose_name='Correo')
	address = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
	city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
	country = models.CharField(max_length=100, blank=True, verbose_name='País')
	phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
	currency = models.CharField(max_length=10, default='BOB', verbose_name='Moneda')
	timezone = models.CharField(max_length=50, default='America/La_Paz', verbose_name='Zona horaria')
	logo = models.ImageField(upload_to='empresas/', blank=True, null=True, verbose_name='Logo')
	is_active = models.BooleanField(default=True, verbose_name='Activo')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Empresa'
		verbose_name_plural = 'Empresas'

	def __str__(self):
		return self.name
