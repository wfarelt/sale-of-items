from django.contrib import admin

from .models import CashBox, CashBoxClosure


@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):
	list_display = ("id", "date", "type", "payment_method", "reference", "amount")
	list_filter = ("type", "payment_method", "reference", "date")
	search_fields = ("description",)
	ordering = ("-date", "-id")


@admin.register(CashBoxClosure)
class CashBoxClosureAdmin(admin.ModelAdmin):
	list_display = ("date", "opening_balance", "total_income", "total_expense", "closing_balance", "is_closed")
	list_filter = ("is_closed", "date")
	search_fields = ("date",)
	ordering = ("-date",)
