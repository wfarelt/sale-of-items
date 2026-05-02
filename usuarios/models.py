from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class Role(models.Model):
    """Modelo de Roles del sistema"""
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('almacen', 'Almacén'),
    )
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name='Nombre del Rol'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Modelo de Usuario extendido"""
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        verbose_name='Rol',
        help_text='Selecciona el rol del usuario'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='¿Activo?'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono'
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Dirección'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.role}"

    @property
    def is_admin(self):
        return not self.is_superuser and self.role.name == 'admin'

    @property
    def is_vendedor(self):
        return self.role.name == 'vendedor'

    @property
    def is_almacen(self):
        return self.role.name == 'almacen'

    @property
    def display_role_name(self):
        if self.is_superuser:
            return 'Superusuario'
        return str(self.role)

    @property
    def display_role_description(self):
        if self.is_superuser:
            return 'Acceso exclusivo al panel de administracion del sistema.'
        return self.role.description


class LoginEvent(models.Model):
    EVENT_LOGIN_SUCCESS = 'login_success'
    EVENT_LOGIN_FAILED = 'login_failed'
    EVENT_LOGOUT = 'logout'

    EVENT_CHOICES = (
        (EVENT_LOGIN_SUCCESS, 'Inicio de sesion exitoso'),
        (EVENT_LOGIN_FAILED, 'Intento fallido'),
        (EVENT_LOGOUT, 'Cierre de sesion'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_events',
        verbose_name='Usuario',
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Username reportado',
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_CHOICES,
        verbose_name='Tipo de evento',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Direccion IP',
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User-Agent',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de evento',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Evento de acceso'
        verbose_name_plural = 'Eventos de acceso'

    def __str__(self):
        username = self.username or (self.user.username if self.user else 'anonimo')
        return f"{self.get_event_type_display()} - {username}"
