#!/usr/bin/env python
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.contrib.auth.hashers import make_password

from empresas.models import Company
from usuarios.models import Role, User


print("Configurando negocio demo...")
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
    print(f"✓ Negocio creado: {company.name}")
else:
    print(f"✓ Negocio existente: {company.name}")

print("\nCreando roles...")
admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': 'Gestion operativa completa'})
vendedor_role, _ = Role.objects.get_or_create(name='vendedor', defaults={'description': 'Gestion de ventas y clientes'})
almacen_role, _ = Role.objects.get_or_create(name='almacen', defaults={'description': 'Gestion de inventario'})
print("✓ Roles listos")

print("\nCreando usuarios base...")
users = [
    ('superadmin', 'superadmin123', 'superadmin@example.com', 'Super', 'Usuario', admin_role, True, True),
    ('admin', 'admin123', 'admin@example.com', 'Administrador', 'Operativo', admin_role, False, False),
    ('vendedor', 'vendedor123', 'vendedor@example.com', 'Juan', 'Vendedor', vendedor_role, False, False),
    ('almacen', 'almacen123', 'almacen@example.com', 'Pedro', 'Inventario', almacen_role, False, False),
]
for username, raw_password, email, first_name, last_name, role, is_staff, is_superuser in users:
    User.objects.update_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'is_staff': is_staff,
            'is_superuser': is_superuser,
            'is_active': True,
            'password': make_password(raw_password),
        },
    )
    print(f"✓ {username} / {raw_password}")

print("\nSetup completado")
