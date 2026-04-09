from django.db import models


class Company(models.Model):
	name = models.CharField(max_length=200, unique=True, verbose_name='Nombre')
	ruc_nit = models.CharField(max_length=30, blank=True, verbose_name='RUC/NIT')
	address = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
	phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
	logo = models.ImageField(upload_to='empresas/', blank=True, null=True, verbose_name='Logo')
	is_active = models.BooleanField(default=True, verbose_name='Activo')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Empresa'
		verbose_name_plural = 'Empresas'

	def __str__(self):
		return self.name
