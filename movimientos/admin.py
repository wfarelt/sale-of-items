from django.contrib import admin

from .models import InventoryMovement, InventoryMovementDetail


class InventoryMovementDetailInline(admin.TabularInline):
	model = InventoryMovementDetail
	extra = 0
	fields = ("product", "quantity")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
	list_display = ("date", "type", "reference", "total_quantity")
	list_filter = ("type", "date")
	search_fields = ("reference", "description", "details__product__name", "details__product__code")
	readonly_fields = ("product", "quantity")
	inlines = [InventoryMovementDetailInline]


@admin.register(InventoryMovementDetail)
class InventoryMovementDetailAdmin(admin.ModelAdmin):
	list_display = ("movement", "product", "quantity")
	search_fields = ("movement__reference", "product__name", "product__code")

# Register your models here.
