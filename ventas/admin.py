from django.contrib import admin

from .models import CommercialCondition, Payment, PaymentMethod, Sale, SaleDetail


class SaleDetailInline(admin.TabularInline):
	model = SaleDetail
	extra = 0
	fields = ("product", "quantity", "price", "subtotal")
	readonly_fields = ("subtotal",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
	list_display = ("id", "client", "date", "commercial_condition", "payment_status", "total")
	list_filter = ("commercial_condition", "status", "date")
	search_fields = ("client__name",)
	readonly_fields = ("total", "created_at", "updated_at")
	inlines = [SaleDetailInline]


@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
	list_display = ("sale", "product", "quantity", "price", "subtotal")
	search_fields = ("sale__id", "product__name")


@admin.register(CommercialCondition)
class CommercialConditionAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "days_due", "is_cash_sale", "is_active")
	list_filter = ("is_cash_sale", "is_active")
	search_fields = ("name", "code")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name", "code")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ("id", "sale", "method", "amount", "paid_at", "recorded_by")
	list_filter = ("method", "paid_at")
	search_fields = ("sale__id", "sale__client__name", "reference")
