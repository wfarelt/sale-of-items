"""
Script para crear datos iniciales en la base de datos.
Ejecutar con: python manage.py shell < setup_initial_data.py
O: python manage.py shell
    >>> exec(open('setup_initial_data.py').read())
"""

from usuarios.models import Role, User
from django.contrib.auth.hashers import make_password

# Crear Roles
print("Creando roles...")
admin_role, created = Role.objects.get_or_create(
    name='admin',
    defaults={
        'description': 'Acceso total al sistema'
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

# Crear usuario administrador
print("\nCreando usuarios de prueba...")
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'role': admin_role,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'password': make_password('admin123')
    }
)
print(f"✓ Usuario Admin {'creado' if created else 'ya existía'} - Contraseña: admin123")

# Crear usuario vendedor
vendedor_user, created = User.objects.get_or_create(
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
print(f"✓ Usuario Vendedor {'creado' if created else 'ya existía'} - Contraseña: vendedor123")

# Crear usuario almacén
almacen_user, created = User.objects.get_or_create(
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
print(f"✓ Usuario Almacén {'creado' if created else 'ya existía'} - Contraseña: almacen123")

print("\n" + "="*50)
print("✅ DATOS INICIALES CREADOS EXITOSAMENTE")
print("="*50)
print("\n📝 Credenciales de acceso al panel admin:")
print("   URL: http://localhost:8000/admin/")
print("\n   Admin:")
print("   → Usuario: admin")
print("   → Contraseña: admin123")
print("\n   Vendedor:")
print("   → Usuario: vendedor")
print("   → Contraseña: vendedor123")
print("\n   Almacén:")
print("   → Usuario: almacen")
print("   → Contraseña: almacen123")
