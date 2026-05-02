from django.contrib import admin

from .models import Acabado, Brand, Category, Formato, IndicacionesUso, M2Caja, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Formato)
class FormatoAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Acabado)
class AcabadoAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(IndicacionesUso)
class IndicacionesUsoAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name", "description")


@admin.register(M2Caja)
class M2CajaAdmin(admin.ModelAdmin):
	list_display = ("value",)
	search_fields = ("value",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "category", "price", "stock", "formato", "acabado", "metros_cuadrados_por_caja")
	list_filter = ("category", "formato", "acabado")
	search_fields = ("code", "name", "description", "formato", "acabado")
