#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

# Importar después de django.setup()
from usuarios.models import Role, User
from django.contrib.auth.hashers import make_password

# Crear Roles
print("Creando roles...")
admin_role, created = Role.objects.get_or_create(
    name='admin',
    defaults={
        'description': 'Puede gestionar todos los modulos operativos y ver reportes'
    }
)
print(f"✓ Rol Admin {'creado' if created else 'ya existía'}")

vendedor_role, created = Role.objects.get_or_create(
    name='vendedor',
    defaults={
        'description': 'Puede gestionar ventas y clientes'
    }
)
print(f"✓ Rol Vendedor {'creado' if created else 'ya existía'}")

almacen_role, created = Role.objects.get_or_create(
    name='almacen',
    defaults={
        'description': 'Puede gestionar inventario y almacén'
    }
)
print(f"✓ Rol Almacén {'creado' if created else 'ya existía'}")

# Crear superusuario
print("\nCreando usuarios de prueba...")
superuser, created = User.objects.update_or_create(
    username='superadmin',
    defaults={
        'email': 'superadmin@example.com',
        'first_name': 'Super',
        'last_name': 'Usuario',
        'role': admin_role,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'password': make_password('superadmin123')
    }
)
print(f"✓ Superusuario {'creado' if created else 'actualizado'} - Contraseña: superadmin123")

# Crear usuario administrador operativo
admin_user, created = User.objects.update_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'first_name': 'Administrador',
        'last_name': 'Operativo',
        'role': admin_role,
        'is_staff': False,
        'is_superuser': False,
        'is_active': True,
        'password': make_password('admin123')
    }
)
print(f"✓ Usuario Admin {'creado' if created else 'actualizado'} - Contraseña: admin123")

# Crear usuario vendedor
vendedor_user, created = User.objects.update_or_create(
    username='vendedor',
    defaults={
        'email': 'vendedor@example.com',
        'first_name': 'Juan',
        'last_name': 'Vendedor',
        'role': vendedor_role,
        'is_active': True,
        'password': make_password('vendedor123')
    }
)
print(f"✓ Usuario Vendedor {'creado' if created else 'actualizado'} - Contraseña: vendedor123")

# Crear usuario almacén
almacen_user, created = User.objects.update_or_create(
    username='almacen',
    defaults={
        'email': 'almacen@example.com',
        'first_name': 'Pedro',
        'last_name': 'Almacén',
        'role': almacen_role,
        'is_active': True,
        'password': make_password('almacen123')
    }
)
print(f"✓ Usuario Almacén {'creado' if created else 'actualizado'} - Contraseña: almacen123")

print("\n" + "="*50)
print("✅ DATOS INICIALES CREADOS EXITOSAMENTE")
print("="*50)
print("\n📝 Credenciales de acceso al panel admin:")
print("   URL: http://localhost:8000/admin/")
print("\n   Superusuario:")
print("   → Usuario: superadmin")
print("   → Contraseña: superadmin123")
print("\n   Admin:")
print("   → Usuario: admin")
print("   → Contraseña: admin123")
print("\n   Vendedor:")
print("   → Usuario: vendedor")
print("   → Contraseña: vendedor123")
print("\n   Almacén:")
print("   → Usuario: almacen")
print("   → Contraseña: almacen123")
