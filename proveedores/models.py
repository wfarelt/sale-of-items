from django.db import models



class Proveedor(models.Model):
    company = models.ForeignKey(
        'empresas.Company',
        on_delete=models.CASCADE,
        related_name='proveedores',
        verbose_name='Empresa'
    )
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre
