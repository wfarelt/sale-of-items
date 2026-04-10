from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = ('name', 'ruc_nit', 'phone', 'email', 'currency', 'is_active', 'created_at')
	list_filter = ('is_active', 'currency', 'created_at')
	search_fields = ('name', 'ruc_nit', 'phone', 'email', 'city')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('name',)
	list_per_page = 25
	fieldsets = (
		('Datos fiscales', {'fields': ('name', 'ruc_nit')}),
		('Contacto', {'fields': ('email', 'phone', 'address', 'city', 'country')}),
		('Configuración', {'fields': ('currency', 'timezone', 'is_active')}),
		('Identidad visual', {'fields': ('logo',)}),
		('Sistema', {'fields': ('created_at', 'updated_at')}),
	)
