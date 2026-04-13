from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import LoginEvent, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description')
        }),
        ('Auditoría', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('company', 'role', 'phone', 'address', 'avatar', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('company', 'role', 'phone', 'address', 'avatar'),
            'classes': ('wide',),
        }),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'company', 'role', 'is_active', 'created_at')
    list_filter = ('company', 'role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginEvent)
class LoginEventAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'event_type', 'username', 'user', 'ip_address')
    list_filter = ('event_type', 'created_at')
    search_fields = ('username', 'user__username', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'username', 'event_type', 'ip_address', 'user_agent', 'created_at')
