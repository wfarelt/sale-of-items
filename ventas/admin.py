from django.contrib import admin

from .models import Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
	model = SaleDetail
	extra = 0
	fields = ("product", "quantity", "price", "subtotal")
	readonly_fields = ("subtotal",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
	list_display = ("id", "client", "date", "payment_type", "total")
	list_filter = ("payment_type", "date")
	search_fields = ("client__name",)
	readonly_fields = ("total", "created_at", "updated_at")
	inlines = [SaleDetailInline]


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
	list_display = ("sale", "product", "quantity", "price", "subtotal")
	search_fields = ("sale__id", "product__name")

# Register your models here.
