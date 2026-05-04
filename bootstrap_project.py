#!/usr/bin/env python
"""Inicializa datos base del proyecto (empresa, roles y usuarios demo).

Uso:
    python bootstrap_project.py
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402

from empresas.models import Company  # noqa: E402
from usuarios.models import Role, User  # noqa: E402


def ensure_company() -> Company:
    company = Company.get_solo()
    if company:
        print(f"OK company existente: {company.name}")
        return company

    company = Company.objects.create(
        name="Porcelanatos Demo",
        ruc_nit="1234567890",
        address="Av. Principal 123",
        city="Santa Cruz",
        country="Bolivia",
        phone="70000000",
        currency="BOB",
        is_active=True,
    )
    print(f"OK company creada: {company.name}")
    return company


def ensure_roles() -> dict[str, Role]:
    role_defaults = {
        "admin": "Gestion operativa completa",
        "vendedor": "Gestion de ventas y clientes",
        "almacen": "Gestion de inventario",
    }
    roles: dict[str, Role] = {}

    for role_name, description in role_defaults.items():
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={"description": description},
        )
        if role.description != description:
            role.description = description
            role.save(update_fields=["description"])
        roles[role_name] = role

    print("OK roles listos")
    return roles


def ensure_users(roles: dict[str, Role]) -> None:
    users = [
        {
            "username": "superadmin",
            "password": "superadmin123",
            "email": "superadmin@example.com",
            "first_name": "Super",
            "last_name": "Usuario",
            "role": roles["admin"],
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@example.com",
            "first_name": "Administrador",
            "last_name": "Operativo",
            "role": roles["admin"],
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "username": "vendedor",
            "password": "vendedor123",
            "email": "vendedor@example.com",
            "first_name": "Juan",
            "last_name": "Vendedor",
            "role": roles["vendedor"],
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "username": "almacen",
            "password": "almacen123",
            "email": "almacen@example.com",
            "first_name": "Pedro",
            "last_name": "Inventario",
            "role": roles["almacen"],
            "is_staff": False,
            "is_superuser": False,
        },
    ]

    for data in users:
        username = data["username"]
        raw_password = data.pop("password")
        data["password"] = make_password(raw_password)
        data["is_active"] = True

        User.objects.update_or_create(
            username=username,
            defaults=data,
        )
        print(f"OK usuario: {username} / {raw_password}")


if __name__ == "__main__":
    print("Inicializando proyecto...")
    ensure_company()
    roles_map = ensure_roles()
    ensure_users(roles_map)
    print("Listo. Datos base creados/actualizados.")
