from django.db import models


class Client(models.Model):
	company = models.ForeignKey(
		'empresas.Company',
		on_delete=models.CASCADE,
		verbose_name='Empresa',
		related_name='clients',
	)
	name = models.CharField(max_length=150, verbose_name="Nombre")
	phone = models.CharField(max_length=20, blank=True, verbose_name="Telefono")
	email = models.EmailField(blank=True, verbose_name="Correo")
	address = models.CharField(max_length=255, blank=True, verbose_name="Direccion")
	nit_ci = models.CharField(max_length=30, verbose_name="NIT/CI")
	is_active = models.BooleanField(default=True, verbose_name="Activo")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		verbose_name = "Cliente"
		verbose_name_plural = "Clientes"
		unique_together = [('company', 'nit_ci')]

	def __str__(self):
		return f"{self.name} ({self.nit_ci})"
