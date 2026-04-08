"""
Script para crear datos iniciales en la base de datos.
Ejecutar con: python manage.py shell < setup_initial_data.py
O: python manage.py shell
    >>> exec(open('setup_initial_data.py').read())
"""

from usuarios.models import Role, User
from django.contrib.auth.hashers import make_password
from clientes.models import Client
from productos.models import Brand, Category, Product
from decimal import Decimal

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

print("\n" + "=" * 60)
print("👥 CREANDO CLIENTES (5)...")
print("=" * 60)

clientes_data = [
    {'name': 'Tienda Sport Central', 'email': 'tienda1@email.com', 'phone': '5551234567', 'nit_ci': 'NIT-001'},
    {'name': 'Distribuidora Deportiva Plus', 'email': 'tienda2@email.com', 'phone': '5559876543', 'nit_ci': 'NIT-002'},
    {'name': 'Zapatería Elite', 'email': 'tienda3@email.com', 'phone': '5552468135', 'nit_ci': 'NIT-003'},
    {'name': 'Ropa Deportiva Total', 'email': 'tienda4@email.com', 'phone': '5553691357', 'nit_ci': 'NIT-004'},
    {'name': 'Mega Sport Store', 'email': 'tienda5@email.com', 'phone': '5557418529', 'nit_ci': 'NIT-005'},
]

for data in clientes_data:
    client, created = Client.objects.get_or_create(
        nit_ci=data['nit_ci'],
        defaults={
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': 'Dirección a especificar',
        }
    )
    print(f"✓ {client.name}")

print("\n" + "=" * 60)
print("🏷️  CREANDO MARCAS (5)...")
print("=" * 60)

marcas_data = [
    'Nike',
    'Adidas', 
    'Puma',
    'Reebok',
    'Asics',
]

for marca_name in marcas_data:
    marca, created = Brand.objects.get_or_create(name=marca_name)
    print(f"✓ {marca.name}")

print("\n" + "=" * 60)
print("📂 CREANDO CATEGORÍAS (5)...")
print("=" * 60)

categorias_data = [
    'Calzado Deportivo',
    'Camisetas y Tops',
    'Pantalones y Shorts',
    'Accesorios',
    'Ropa de Abrigo',
]

categorias = {}
for cat_name in categorias_data:
    cat, created = Category.objects.get_or_create(name=cat_name)
    categorias[cat_name] = cat
    print(f"✓ {cat.name}")

print("\n" + "=" * 60)
print("📦 CREANDO PRODUCTOS (10)...")
print("=" * 60)

# Obtener marcas para referencias
marcas_dict = {marca.name: marca for marca in Brand.objects.all()}

productos_data = [
    {'name': 'Zapatilla Running Ultralight', 'category': 'Calzado Deportivo', 'brand': 'Nike', 'price': Decimal('119.99'), 'stock': 45, 'code': 'PROD-001', 'size': 'M', 'color': 'Negro'},
    {'name': 'Botín Football Pro', 'category': 'Calzado Deportivo', 'brand': 'Adidas', 'price': Decimal('159.99'), 'stock': 30, 'code': 'PROD-002', 'size': 'L', 'color': 'Blanco'},
    {'name': 'Zapatilla Casual Urbana', 'category': 'Calzado Deportivo', 'brand': 'Puma', 'price': Decimal('99.99'), 'stock': 50, 'code': 'PROD-003', 'size': 'M', 'color': 'Gris'},
    {'name': 'Camiseta Técnica Transpirable', 'category': 'Camisetas y Tops', 'brand': 'Nike', 'price': Decimal('44.99'), 'stock': 80, 'code': 'PROD-004', 'size': 'M', 'color': 'Azul'},
    {'name': 'Camiseta Básica Deportiva', 'category': 'Camisetas y Tops', 'brand': 'Adidas', 'price': Decimal('34.99'), 'stock': 100, 'code': 'PROD-005', 'size': 'L', 'color': 'Blanco'},
    {'name': 'Short Entrenamiento Ligero', 'category': 'Pantalones y Shorts', 'brand': 'Reebok', 'price': Decimal('49.99'), 'stock': 60, 'code': 'PROD-006', 'size': 'M', 'color': 'Negro'},
    {'name': 'Pantalón Deportivo Clásico', 'category': 'Pantalones y Shorts', 'brand': 'Asics', 'price': Decimal('79.99'), 'stock': 40, 'code': 'PROD-007', 'size': 'L', 'color': 'Gris'},
    {'name': 'Mochila Deportiva 25L', 'category': 'Accesorios', 'brand': 'Nike', 'price': Decimal('89.99'), 'stock': 35, 'code': 'PROD-008', 'size': 'M', 'color': 'Negro'},
    {'name': 'Sudadera Hoodie Premium', 'category': 'Ropa de Abrigo', 'brand': 'Adidas', 'price': Decimal('99.99'), 'stock': 25, 'code': 'PROD-009', 'size': 'L', 'color': 'Gris'},
    {'name': 'Chaqueta Cortaviento Impermeable', 'category': 'Ropa de Abrigo', 'brand': 'Puma', 'price': Decimal('129.99'), 'stock': 20, 'code': 'PROD-010', 'size': 'XL', 'color': 'Rojo'},
]

for prod_data in productos_data:
    categoria = categorias.get(prod_data['category'])
    marca = marcas_dict.get(prod_data['brand'])
    
    if categoria and marca:
        producto, created = Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'category': categoria,
                'brand': marca,
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'size': prod_data['size'],
                'color': prod_data['color'],
                'description': f"Producto deportivo de calidad {marca.name}",
            }
        )
        print(f"✓ {producto.name} - Bs {producto.price}")

print(f"\n" + "=" * 60)
print("✅ DATOS INICIALES CREADOS EXITOSAMENTE")
print("=" * 60)
print("\n� Credenciales de acceso al panel admin:")
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
