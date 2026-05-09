#!/usr/bin/env python
"""Carga datos base de catalogo, productos, clientes y proveedores.

Uso:
    python script_datos_de_prueba.py
"""

from __future__ import annotations

import os
import sys
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from clientes.models import Client  # noqa: E402
from productos.models import (  # noqa: E402
    Acabado,
    Brand,
    Category,
    Formato,
    IndicacionesUso,
    M2Caja,
    Product,
)
from proveedores.models import Proveedor  # noqa: E402


CATEGORIES = [
    "Porcelanato",
    "Ceramica",
    "Revestimiento",
    "Piso Vinilico",
]

BRANDS = [
    "Keramica",
    "Coboce",
    "Cejatel",
    "Incefra",
]

FORMATOS = [
    "30x60",
    "60x60",
    "60x120",
    "20x120",
]

ACABADOS = [
    "Brillante",
    "Mate",
    "Satinado",
    "Texturizado",
]

INDICACIONES = [
    {
        "name": "Interior",
        "description": "Uso recomendado en espacios interiores secos.",
    },
    {
        "name": "Interior/Exterior",
        "description": "Apto para zonas interiores y exteriores con trafico medio.",
    },
    {
        "name": "Alto trafico",
        "description": "Recomendado para areas comerciales y de alto transito.",
    },
]

M2_CAJA_VALUES = [
    Decimal("1.44"),
    Decimal("1.62"),
    Decimal("1.80"),
    Decimal("2.16"),
]

PRODUCTS = [
    {
        "code": "POR-6060-MAT-GRIS",
        "name": "Porcelanato 60x60 Gris Mate",
        "description": "Porcelanato rectificado para interiores de estilo moderno.",
        "price": Decimal("85.00"),
        "stock": Decimal("120.00"),
        "stock_minimo": 20,
        "color": "Gris",
        "category": "Porcelanato",
        "brand": "Keramica",
        "formato": "60x60",
        "acabado": "Mate",
        "indicaciones_uso": "Interior",
        "m2_caja": Decimal("1.44"),
    },
    {
        "code": "POR-60120-BRI-BLAN",
        "name": "Porcelanato 60x120 Blanco Brillante",
        "description": "Ideal para ambientes amplios y de alta luminosidad.",
        "price": Decimal("135.00"),
        "stock": Decimal("80.00"),
        "stock_minimo": 15,
        "color": "Blanco",
        "category": "Porcelanato",
        "brand": "Incefra",
        "formato": "60x120",
        "acabado": "Brillante",
        "indicaciones_uso": "Interior",
        "m2_caja": Decimal("1.80"),
    },
    {
        "code": "CER-3060-SAT-BEIG",
        "name": "Ceramica 30x60 Beige Satinado",
        "description": "Revestimiento de facil limpieza para bano y cocina.",
        "price": Decimal("58.00"),
        "stock": Decimal("150.00"),
        "stock_minimo": 25,
        "color": "Beige",
        "category": "Ceramica",
        "brand": "Cejatel",
        "formato": "30x60",
        "acabado": "Satinado",
        "indicaciones_uso": "Interior",
        "m2_caja": Decimal("1.62"),
    },
    {
        "code": "REV-3060-TEX-ARENA",
        "name": "Revestimiento 30x60 Arena Texturizado",
        "description": "Pared decorativa con textura suave y tono arena.",
        "price": Decimal("62.00"),
        "stock": Decimal("95.00"),
        "stock_minimo": 18,
        "color": "Arena",
        "category": "Revestimiento",
        "brand": "Coboce",
        "formato": "30x60",
        "acabado": "Texturizado",
        "indicaciones_uso": "Interior/Exterior",
        "m2_caja": Decimal("1.62"),
    },
    {
        "code": "VIN-20120-MAT-MADERA",
        "name": "Piso Vinilico 20x120 Madera Mate",
        "description": "Listones vinilicos resistentes a humedad para uso residencial.",
        "price": Decimal("92.00"),
        "stock": Decimal("60.00"),
        "stock_minimo": 12,
        "color": "Madera Natural",
        "category": "Piso Vinilico",
        "brand": "Keramica",
        "formato": "20x120",
        "acabado": "Mate",
        "indicaciones_uso": "Alto trafico",
        "m2_caja": Decimal("2.16"),
    },
]

# Completa hasta 15 productos de prueba en total.
for idx in range(6, 16):
    category = CATEGORIES[(idx - 1) % len(CATEGORIES)]
    brand = BRANDS[(idx - 1) % len(BRANDS)]
    formato = FORMATOS[(idx - 1) % len(FORMATOS)]
    acabado = ACABADOS[(idx - 1) % len(ACABADOS)]
    indicacion = INDICACIONES[(idx - 1) % len(INDICACIONES)]["name"]
    m2_value = M2_CAJA_VALUES[(idx - 1) % len(M2_CAJA_VALUES)]

    PRODUCTS.append(
        {
            "code": f"PRD-{idx:04d}",
            "name": f"Producto Demo {idx:02d}",
            "description": f"Producto de prueba {idx:02d} para carga inicial.",
            "price": Decimal(str(45 + (idx * 7))),
            "stock": Decimal(str(20 + (idx * 11))),
            "stock_minimo": 5 + (idx % 10),
            "color": "Neutro",
            "category": category,
            "brand": brand,
            "formato": formato,
            "acabado": acabado,
            "indicaciones_uso": indicacion,
            "m2_caja": m2_value,
        }
    )

CLIENTS = [
    {
        "name": "Constructora Altiplano SRL",
        "phone": "70012345",
        "email": "compras@altiplano.com",
        "address": "Av. Banzer #123",
        "nit_ci": "1020304011",
    },
    {
        "name": "Mariana Rojas",
        "phone": "72155510",
        "email": "mariana.rojas@example.com",
        "address": "Zona Norte, Calle 5",
        "nit_ci": "8899776",
    },
    {
        "name": "Inmobiliaria Horizonte",
        "phone": "75000122",
        "email": "contacto@horizonte.bo",
        "address": "Av. Cristo Redentor #890",
        "nit_ci": "5566778899",
    },
]

# Completa hasta 20 clientes de prueba en total.
for idx in range(4, 21):
    CLIENTS.append(
        {
            "name": f"Cliente Demo {idx:02d}",
            "phone": f"7{idx:07d}",
            "email": f"cliente{idx:02d}@demo.com",
            "address": f"Zona Demo, Calle {idx}",
            "nit_ci": f"900000{idx:02d}",
        }
    )

SUPPLIERS = [
    {
        "nombre": "Proveedor Ceramicos del Sur",
        "contacto": "Luis Calderon",
        "direccion": "Parque Industrial, Manzano 4",
        "telefono": "33445566",
        "email": "ventas@ceramicosdelsur.com",
        "observaciones": "Despachos semanales con previa coordinacion.",
    },
    {
        "nombre": "Distribuidora Andina",
        "contacto": "Carla Mendoza",
        "direccion": "Av. Doble Via La Guardia Km 7",
        "telefono": "31234567",
        "email": "pedidos@andina.bo",
        "observaciones": "Maneja formatos grandes y stock permanente.",
    },
    {
        "nombre": "Importadora PisoHome",
        "contacto": "Ernesto Quiroga",
        "direccion": "Zona Equipetrol, Calle 3 Oeste",
        "telefono": "39887766",
        "email": "importaciones@pisohome.com",
        "observaciones": "Especialista en piso vinilico y revestimientos premium.",
    },
]

# Completa hasta 10 proveedores de prueba en total.
for idx in range(4, 11):
    SUPPLIERS.append(
        {
            "nombre": f"Proveedor Demo {idx:02d}",
            "contacto": f"Contacto {idx:02d}",
            "direccion": f"Parque Industrial, Bloque {idx}",
            "telefono": f"3{idx:07d}",
            "email": f"proveedor{idx:02d}@demo.com",
            "observaciones": "Proveedor generado automaticamente para pruebas.",
        }
    )


def ensure_named_catalog(model, values: list[str], label: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for value in values:
        obj, _ = model.objects.get_or_create(name=value, defaults={"is_active": True})
        if not obj.is_active:
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        result[value] = obj
    print(f"OK {label}: {len(result)}")
    return result


def ensure_indicaciones() -> dict[str, IndicacionesUso]:
    result: dict[str, IndicacionesUso] = {}
    for item in INDICACIONES:
        obj, _ = IndicacionesUso.objects.update_or_create(
            name=item["name"],
            defaults={
                "description": item["description"],
                "is_active": True,
            },
        )
        result[item["name"]] = obj
    print(f"OK indicaciones: {len(result)}")
    return result


def ensure_m2_caja() -> dict[Decimal, M2Caja]:
    result: dict[Decimal, M2Caja] = {}
    for value in M2_CAJA_VALUES:
        obj, _ = M2Caja.objects.get_or_create(value=value, defaults={"is_active": True})
        if not obj.is_active:
            obj.is_active = True
            obj.save(update_fields=["is_active"])
        result[value] = obj
    print(f"OK m2 por caja: {len(result)}")
    return result


def ensure_products(
    categories: dict[str, Category],
    brands: dict[str, Brand],
    formatos: dict[str, Formato],
    acabados: dict[str, Acabado],
    indicaciones: dict[str, IndicacionesUso],
    m2_caja: dict[Decimal, M2Caja],
) -> None:
    total = 0
    for item in PRODUCTS:
        lookup = {"code": item["code"]} if item.get("code") else {"name": item["name"]}

        defaults = {
            "name": item["name"],
            "description": item["description"],
            "price": item["price"],
            "stock": item["stock"],
            "stock_minimo": item["stock_minimo"],
            "color": item["color"],
            "category": categories[item["category"]],
            "brand": brands[item["brand"]],
            "formato": formatos[item["formato"]],
            "acabado": acabados[item["acabado"]],
            "indicaciones_uso": indicaciones[item["indicaciones_uso"]],
            "metros_cuadrados_por_caja": m2_caja[item["m2_caja"]],
            "is_active": True,
        }

        Product.objects.update_or_create(**lookup, defaults=defaults)
        total += 1

    print(f"OK productos: {total}")


def ensure_clients() -> None:
    total = 0
    for item in CLIENTS:
        Client.objects.update_or_create(
            nit_ci=item["nit_ci"],
            defaults={
                "name": item["name"],
                "phone": item["phone"],
                "email": item["email"],
                "address": item["address"],
                "is_active": True,
            },
        )
        total += 1
    print(f"OK clientes: {total}")


def ensure_suppliers() -> None:
    total = 0
    for item in SUPPLIERS:
        Proveedor.objects.update_or_create(
            nombre=item["nombre"],
            defaults={
                "contacto": item["contacto"],
                "direccion": item["direccion"],
                "telefono": item["telefono"],
                "email": item["email"],
                "observaciones": item["observaciones"],
                "activo": True,
            },
        )
        total += 1
    print(f"OK proveedores: {total}")


@transaction.atomic
def load_data() -> None:
    categories = ensure_named_catalog(Category, CATEGORIES, "categorias")
    brands = ensure_named_catalog(Brand, BRANDS, "marcas")
    formatos = ensure_named_catalog(Formato, FORMATOS, "formatos")
    acabados = ensure_named_catalog(Acabado, ACABADOS, "acabados")
    indicaciones = ensure_indicaciones()
    m2_caja = ensure_m2_caja()

    ensure_products(categories, brands, formatos, acabados, indicaciones, m2_caja)
    ensure_clients()
    ensure_suppliers()


if __name__ == "__main__":
    print("Cargando catalogos, productos, clientes y proveedores...")
    load_data()
    print("Listo. Datos creados/actualizados correctamente.")