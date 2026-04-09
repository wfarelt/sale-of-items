from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = ('name', 'ruc_nit', 'phone', 'is_active', 'created_at')
	list_filter = ('is_active',)
	search_fields = ('name', 'ruc_nit')
