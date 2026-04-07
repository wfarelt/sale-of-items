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
	list_display = ("code", "name", "category", "brand", "price", "stock", "size", "color")
	list_filter = ("category", "brand", "size")
	search_fields = ("code", "name", "description", "color")
