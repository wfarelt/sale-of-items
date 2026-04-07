from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ("name", "nit_ci", "phone", "email")
	search_fields = ("name", "nit_ci", "phone", "email")
