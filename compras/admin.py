from django.contrib import admin

from .models import Purchase, PurchaseDetail


class PurchaseDetailInline(admin.TabularInline):
	model = PurchaseDetail
	extra = 0
	fields = ("product", "quantity", "cost_price", "sale_price", "subtotal")
	readonly_fields = ("subtotal", "created_at")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
	list_display = ("id", "supplier", "invoice_number", "date", "total", "status")
	list_filter = ("status", "date")
	search_fields = ("supplier__nombre", "invoice_number")
	readonly_fields = ("total", "created_at", "updated_at")
	inlines = [PurchaseDetailInline]
	fieldsets = (
		("Información", {
			"fields": ("supplier", "invoice_number", "date", "status")
		}),
		("Detalles", {
			"fields": ("total",)
		}),
		("Auditoría", {
			"fields": ("created_at", "updated_at"),
			"classes": ("collapse",)
		}),
	)


@admin.register(PurchaseDetail)
class PurchaseDetailAdmin(admin.ModelAdmin):
	list_display = ("purchase", "product", "quantity", "cost_price", "sale_price", "subtotal")
	list_filter = ("purchase", "product")
	search_fields = ("purchase__id", "product__name")
	readonly_fields = ("subtotal", "created_at")
