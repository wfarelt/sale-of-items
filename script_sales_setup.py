#!/usr/bin/env python
"""Carga condiciones comerciales y metodos de pago.

Uso:
    python script_sales_setup.py
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from ventas.models import CommercialCondition, PaymentMethod  # noqa: E402


COMMERCIAL_CONDITIONS = [
    {
        "code": CommercialCondition.CODE_CASH,
        "name": "Contado",
        "days_due": 0,
        "is_cash_sale": True,
    },
    {
        "code": CommercialCondition.CODE_CREDIT_7,
        "name": "Credito 7 dias",
        "days_due": 7,
        "is_cash_sale": False,
    },
    {
        "code": CommercialCondition.CODE_CREDIT_15,
        "name": "Credito 15 dias",
        "days_due": 15,
        "is_cash_sale": False,
    },
    {
        "code": CommercialCondition.CODE_CREDIT_30,
        "name": "Credito 30 dias",
        "days_due": 30,
        "is_cash_sale": False,
    },
]

PAYMENT_METHODS = [
    {"code": PaymentMethod.CODE_CASH, "name": "Efectivo"},
    {"code": PaymentMethod.CODE_QR, "name": "QR"},
    {"code": PaymentMethod.CODE_TRANSFER, "name": "Transferencia"},
    {"code": PaymentMethod.CODE_CARD, "name": "Tarjeta"},
]


def ensure_commercial_conditions() -> None:
    total = 0
    for item in COMMERCIAL_CONDITIONS:
        CommercialCondition.objects.update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "days_due": item["days_due"],
                "is_cash_sale": item["is_cash_sale"],
                "is_active": True,
            },
        )
        total += 1
    print(f"OK condiciones comerciales: {total}")


def ensure_payment_methods() -> None:
    total = 0
    for item in PAYMENT_METHODS:
        PaymentMethod.objects.update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "is_active": True,
            },
        )
        total += 1
    print(f"OK metodos de pago: {total}")


@transaction.atomic
def load_data() -> None:
    ensure_commercial_conditions()
    ensure_payment_methods()


if __name__ == "__main__":
    print("Cargando condiciones comerciales y metodos de pago...")
    load_data()
    print("Listo. Datos creados/actualizados correctamente.")