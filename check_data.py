#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from clientes.models import Client
from productos.models import Brand, Category, Product
from usuarios.models import User, Role

print("=== CONTEO DE DATOS ===")
print(f"Usuarios: {User.objects.count()}")
print(f"Roles: {Role.objects.count()}")
print(f"Clientes: {Client.objects.count()}")
print(f"Marcas: {Brand.objects.count()}")
print(f"Categorías: {Category.objects.count()}")
print(f"Productos: {Product.objects.count()}")

print("\n=== PRIMEROS 3 CLIENTES ===")
for client in Client.objects.all()[:3]:
    print(f"- {client.name} (NIT: {client.nit_ci}, Email: {client.email})")

print("\n=== CATEGORÍAS ===")
for cat in Category.objects.all():
    print(f"- {cat.name}")

print("\n=== PRIMEROS 5 PRODUCTOS ===")
for prod in Product.objects.all()[:5]:
    try:
        print(f"- {prod.name} (${prod.price}, Stock: {prod.stock}, Color: {prod.color})")
    except Exception as e:
        print(f"- Error printing product: {e}")
