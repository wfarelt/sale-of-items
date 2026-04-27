from django.contrib import admin

from .models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "category", "price", "formato", "acabado", "metros_cuadrados_por_caja")
	list_filter = ("category", "formato", "acabado")
	search_fields = ("code", "name", "description", "formato", "acabado")
