"""
Script para crear datos iniciales en la base de datos.
Ejecutar con: python manage.py shell < setup_initial_data.py
O: python manage.py shell
    >>> exec(open('setup_initial_data.py').read())
"""

from decimal import Decimal

from django.contrib.auth.hashers import make_password

from clientes.models import Client
from empresas.models import Company
from productos.models import Brand, Category, Product
from usuarios.models import Role, User

company = Company.get_solo()
if not company:
    company = Company.objects.create(
        name='Porcelanatos Demo',
        ruc_nit='1234567890',
        address='Av. Principal 123',
        city='Santa Cruz',
        country='Bolivia',
        phone='70000000',
        currency='BOB',
    )

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

print("\n" + "=" * 60)
print("👥 CREANDO CLIENTES (5)...")
print("=" * 60)

clientes_data = [
    {'name': 'Constructora Andina', 'email': 'cliente1@email.com', 'phone': '5551234567', 'nit_ci': 'NIT-001'},
    {'name': 'Arquitectura Norte', 'email': 'cliente2@email.com', 'phone': '5559876543', 'nit_ci': 'NIT-002'},
    {'name': 'Ferretería Central', 'email': 'cliente3@email.com', 'phone': '5552468135', 'nit_ci': 'NIT-003'},
    {'name': 'Diseño y Acabados', 'email': 'cliente4@email.com', 'phone': '5553691357', 'nit_ci': 'NIT-004'},
    {'name': 'Remodelaciones Sur', 'email': 'cliente5@email.com', 'phone': '5557418529', 'nit_ci': 'NIT-005'},
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

marcas_data = ['Cejatel', 'Portobello', 'Elizabeth', 'Cañadon', 'Incefra']

for marca_name in marcas_data:
    marca, created = Brand.objects.get_or_create(name=marca_name)
    print(f"✓ {marca.name}")

print("\n" + "=" * 60)
print("📂 CREANDO CATEGORÍAS (5)...")
print("=" * 60)

categorias_data = ['Piso Interior', 'Muro Interior', 'Exterior', 'Baño', 'Decorativo']

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
    {'name': 'Porcelanato Cemento Gris 60x60', 'category': 'Piso Interior', 'brand': 'Cejatel', 'price': Decimal('89.90'), 'stock': 45, 'code': 'POR-001', 'formato': '60x60', 'acabado': 'Mate', 'color': 'Gris', 'm2': Decimal('1.44')},
    {'name': 'Porcelanato Mármol Blanco 60x120', 'category': 'Piso Interior', 'brand': 'Portobello', 'price': Decimal('139.90'), 'stock': 30, 'code': 'POR-002', 'formato': '60x120', 'acabado': 'Pulido', 'color': 'Blanco', 'm2': Decimal('1.44')},
    {'name': 'Revestimiento Arena Beige 30x60', 'category': 'Muro Interior', 'brand': 'Elizabeth', 'price': Decimal('74.90'), 'stock': 50, 'code': 'POR-003', 'formato': '30x60', 'acabado': 'Mate', 'color': 'Beige', 'm2': Decimal('1.62')},
    {'name': 'Porcelanato Terra Grafito 75x75', 'category': 'Exterior', 'brand': 'Incefra', 'price': Decimal('119.90'), 'stock': 22, 'code': 'POR-004', 'formato': '75x75', 'acabado': 'Antideslizante', 'color': 'Grafito', 'm2': Decimal('1.13')},
    {'name': 'Revestimiento Calacatta 30x90', 'category': 'Baño', 'brand': 'Cañadon', 'price': Decimal('99.90'), 'stock': 35, 'code': 'POR-005', 'formato': '30x90', 'acabado': 'Brillante', 'color': 'Blanco', 'm2': Decimal('1.35')},
    {'name': 'Porcelanato Roble Natural 20x120', 'category': 'Piso Interior', 'brand': 'Elizabeth', 'price': Decimal('129.90'), 'stock': 28, 'code': 'POR-006', 'formato': '20x120', 'acabado': 'Mate', 'color': 'Madera', 'm2': Decimal('1.44')},
    {'name': 'Mosaico Hexagonal Negro 25x29', 'category': 'Decorativo', 'brand': 'Portobello', 'price': Decimal('109.90'), 'stock': 18, 'code': 'POR-007', 'formato': '25x29', 'acabado': 'Mate', 'color': 'Negro', 'm2': Decimal('0.96')},
    {'name': 'Porcelanato Concreto Humo 90x90', 'category': 'Piso Interior', 'brand': 'Cejatel', 'price': Decimal('149.90'), 'stock': 16, 'code': 'POR-008', 'formato': '90x90', 'acabado': 'Mate', 'color': 'Gris', 'm2': Decimal('1.62')},
    {'name': 'Revestimiento Texturizado Arena 32x58', 'category': 'Muro Interior', 'brand': 'Incefra', 'price': Decimal('69.90'), 'stock': 42, 'code': 'POR-009', 'formato': '32x58', 'acabado': 'Texturizado', 'color': 'Arena', 'm2': Decimal('1.48')},
    {'name': 'Porcelanato Piedra Ceniza 60x60', 'category': 'Exterior', 'brand': 'Cañadon', 'price': Decimal('94.90'), 'stock': 27, 'code': 'POR-010', 'formato': '60x60', 'acabado': 'Antideslizante', 'color': 'Ceniza', 'm2': Decimal('1.44')},
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
                'formato': prod_data['formato'],
                'acabado': prod_data['acabado'],
                'color': prod_data['color'],
                'metros_cuadrados_por_caja': prod_data['m2'],
                'stock_minimo': 8,
                'indicaciones_uso': 'Uso recomendado en proyectos residenciales y comerciales.',
                'description': f"Porcelanato de alta calidad marca {marca.name}",
            }
        )
        print(f"✓ {producto.name} - Bs {producto.price}")

print(f"\n" + "=" * 60)
print("✅ DATOS INICIALES CREADOS EXITOSAMENTE")
print("=" * 60)
print("\n� Credenciales de acceso al panel admin:")
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
print("\n   Inventario:")
print("   → Usuario: almacen")
print("   → Contraseña: almacen123")
