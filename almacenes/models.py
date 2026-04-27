from django.db import models



class Almacen(models.Model):
    company = models.ForeignKey(
        'empresas.Company',
        on_delete=models.CASCADE,
        related_name='almacenes',
        verbose_name='Empresa'
    )
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre


# Relación Producto-Almacen-Proveedor (Stock)
from productos.models import Product
from proveedores.models import Proveedor

class Stock(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='stocks')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='stocks')
    lote = models.CharField(max_length=50, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_ingreso = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('producto', 'almacen', 'lote')

    def __str__(self):
        return f"{self.producto} - {self.almacen} - Lote: {self.lote}"
