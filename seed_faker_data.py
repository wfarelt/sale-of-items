#!/usr/bin/env python
"""Genera datos de prueba para el negocio único de porcelanatos."""

import argparse
import os
import random
import sys
from decimal import Decimal, ROUND_HALF_UP

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))

import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402
from django.db import transaction  # noqa: E402

from caja.models import CashBox  # noqa: E402
from clientes.models import Client  # noqa: E402
from compras.models import Purchase, PurchaseDetail  # noqa: E402
from empresas.models import Company  # noqa: E402
from productos.models import Acabado, Brand, Category, Formato, IndicacionesUso, M2Caja, Product  # noqa: E402
from proveedores.models import Proveedor  # noqa: E402
from usuarios.models import Role, User  # noqa: E402
from ventas.models import Sale, SaleDetail  # noqa: E402

try:
    from faker import Faker
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Faker no esta instalado. Ejecuta: pip install Faker"
    ) from exc


PAYMENT_CHOICES = ["cash", "qr", "transferencia"]
FORMATS = ["60x60", "60x120", "75x75", "30x60", "20x120", "32x58"]
FINISHES = ["Mate", "Pulido", "Brillante", "Antideslizante", "Texturizado"]
COLORS = ["Blanco", "Beige", "Gris", "Grafito", "Arena", "Madera"]


class Seeder:
    def __init__(self, *, locale: str, seed: int) -> None:
        self.fake = Faker(locale)
        random.seed(seed)
        Faker.seed(seed)

    @staticmethod
    def ensure_company(name: str) -> "Company":
        company = Company.get_solo()
        if company:
            return company
        return Company.objects.create(
            name=name,
            ruc_nit="0000000000",
            address="Dirección de prueba",
            phone="00000000",
            is_active=True,
        )

    @staticmethod
    def _money(value: float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def ensure_roles(self) -> dict[str, Role]:
        role_defaults = {
            "admin": "Puede gestionar todos los modulos operativos y ver reportes",
            "vendedor": "Puede gestionar ventas y clientes",
            "almacen": "Puede gestionar inventario y almacen",
        }
        roles: dict[str, Role] = {}
        for role_name, role_desc in role_defaults.items():
            role, _ = Role.objects.get_or_create(name=role_name, defaults={"description": role_desc})
            roles[role_name] = role
        return roles

    def ensure_base_users(self, roles: dict[str, Role]) -> None:
        defaults = [
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
                "first_name": "Admin",
                "last_name": "Operativo",
                "role": roles["admin"],
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "vendedor",
                "password": "vendedor123",
                "email": "vendedor@example.com",
                "first_name": "Usuario",
                "last_name": "Vendedor",
                "role": roles["vendedor"],
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "almacen",
                "password": "almacen123",
                "email": "almacen@example.com",
                "first_name": "Usuario",
                "last_name": "Almacen",
                "role": roles["almacen"],
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        for user_data in defaults:
            username = user_data.pop("username")
            raw_password = user_data.pop("password")
            user_data["password"] = make_password(raw_password)
            user_data["is_active"] = True
            User.objects.update_or_create(username=username, defaults=user_data)

    def create_vendedores(self, *, roles: dict[str, Role], count: int) -> list[User]:
        vendedores = list(User.objects.filter(role=roles["vendedor"], is_active=True))
        target = max(count, 1)

        while len(vendedores) < target:
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"vend_{self.fake.unique.bothify(text='??####').lower()}"
            vendedor = User.objects.create(
                username=username,
                email=self.fake.unique.email(),
                first_name=first_name,
                last_name=last_name,
                role=roles["vendedor"],
                is_active=True,
                is_staff=False,
                is_superuser=False,
                phone=self.fake.phone_number()[:15],
                address=self.fake.address()[:255],
                password=make_password("vendedor123"),
            )
            vendedores.append(vendedor)

        return vendedores

    def create_clients(self, count: int) -> int:
        created = 0
        for _ in range(count):
            nit_ci = f"NIT-{self.fake.unique.bothify(text='######')}"
            Client.objects.create(
                name=self.fake.company()[:150],
                phone=self.fake.phone_number()[:20],
                email=self.fake.unique.company_email(),
                address=self.fake.address()[:255],
                nit_ci=nit_ci,
                is_active=True,
            )
            created += 1
        return created

    def ensure_catalog(self) -> tuple[list[Category], list[Brand]]:
        base_categories = [
            "Piso Interior",
            "Muro Interior",
            "Exterior",
            "Baño",
            "Decorativo",
        ]
        base_brands = ["Cejatel", "Portobello", "Elizabeth", "Incefra", "Cañadon", "Castel"]

        categories = []
        brands = []

        for cat_name in base_categories:
            category, _ = Category.objects.get_or_create(name=cat_name, defaults={"is_active": True})
            categories.append(category)

        for brand_name in base_brands:
            brand, _ = Brand.objects.get_or_create(name=brand_name, defaults={"is_active": True})
            brands.append(brand)

        return categories, brands

    def create_products(self, *, count: int, categories: list[Category], brands: list[Brand]) -> int:
        created = 0
        for _ in range(count):
            code = f"PRD-{self.fake.unique.bothify(text='#####')}"
            formato = random.choice(FORMATS)
            acabado = random.choice(FINISHES)
            color = random.choice(COLORS)
            formato_obj, _ = Formato.objects.get_or_create(name=formato, defaults={"is_active": True})
            acabado_obj, _ = Acabado.objects.get_or_create(name=acabado, defaults={"is_active": True})
            indicacion_obj, _ = IndicacionesUso.objects.get_or_create(
                name="Interior residencial",
                defaults={
                    "description": "Uso recomendado en interior y proyectos residenciales.",
                    "is_active": True,
                },
            )
            m2_valor = self._money(random.uniform(1.10, 1.80))
            m2_obj, _ = M2Caja.objects.get_or_create(value=m2_valor, defaults={"is_active": True})
            name = f"Porcelanato {color} {formato}"
            product = Product.objects.create(
                code=code,
                name=name[:150],
                description=self.fake.sentence(nb_words=12),
                price=self._money(random.uniform(20, 350)),
                stock=self._money(random.uniform(10, 80)),
                formato=formato_obj,
                acabado=acabado_obj,
                color=color,
                metros_cuadrados_por_caja=m2_obj,
                stock_minimo=random.randint(5, 12),
                indicaciones_uso=indicacion_obj,
                brand=random.choice(brands),
                category=random.choice(categories),
                is_active=True,
            )
            created += 1

            if product.stock <= 0:
                product.stock = self._money(random.uniform(5, 20))
                product.save(update_fields=["stock"])

        return created

    def create_purchases(self, *, count: int, max_items: int) -> int:
        products = list(Product.objects.filter(is_active=True))
        suppliers = list(Proveedor.objects.filter(activo=True))
        if not products:
            return 0
        if not suppliers:
            return 0

        created = 0
        for _ in range(count):
            purchase = Purchase.objects.create(
                supplier=random.choice(suppliers),
                invoice_number=f"FAC-{self.fake.unique.bothify(text='######')}",
                status="recibida",
            )

            picked = random.sample(products, k=min(len(products), random.randint(1, max_items)))
            for product in picked:
                quantity = self._money(random.uniform(3, 18))
                cost_price = self._money(random.uniform(12, 180))
                margin = Decimal(str(random.uniform(1.25, 1.60)))
                sale_price = (cost_price * margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                PurchaseDetail.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=quantity,
                    cost_price=cost_price,
                    sale_price=sale_price,
                )

            purchase.calculate_total()
            purchase.apply_inventory_update()
            created += 1

        return created

    def create_sales(self, *, count: int, max_items: int, sellers: list[User]) -> int:
        clients = list(Client.objects.filter(is_active=True))
        products = list(Product.objects.filter(is_active=True))
        if not clients or not products:
            return 0

        created = 0
        for _ in range(count):
            available = [p for p in products if p.stock > 0]
            if not available:
                break

            sale = Sale.objects.create(
                client=random.choice(clients),
                seller=random.choice(sellers) if sellers else None,
                status=Sale.STATUS_CONFIRMED,
                payment_type=random.choice(PAYMENT_CHOICES),
            )

            picked = random.sample(available, k=min(len(available), random.randint(1, max_items)))
            detail_created = 0
            for product in picked:
                if product.stock <= 0:
                    continue
                max_qty = min(float(product.stock), 4.0)
                if max_qty < 0.01:
                    continue
                quantity = self._money(random.uniform(0.01, max_qty))
                if quantity <= 0:
                    continue
                SaleDetail.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )
                detail_created += 1

            if detail_created == 0:
                sale.delete()
                continue

            sale.calculate_total()
            sale.apply_inventory_output()
            try:
                CashBox.register_sale(sale)
            except ValidationError:
                pass

            for refreshed in Product.objects.filter(id__in=[p.id for p in picked]):
                for idx, old in enumerate(products):
                    if old.id == refreshed.id:
                        products[idx] = refreshed
                        break

            created += 1

        return created


@transaction.atomic
def run(args: argparse.Namespace) -> None:
    seeder = Seeder(locale=args.locale, seed=args.seed)

    company = seeder.ensure_company(args.company)

    roles = seeder.ensure_roles()
    seeder.ensure_base_users(roles)
    sellers = seeder.create_vendedores(roles=roles, count=args.sellers)

    categories, brands = seeder.ensure_catalog()

    created_clients = seeder.create_clients(args.clients)
    created_products = seeder.create_products(count=args.products, categories=categories, brands=brands)
    created_purchases = seeder.create_purchases(count=args.purchases, max_items=args.max_items)
    created_sales = seeder.create_sales(count=args.sales, max_items=args.max_items, sellers=sellers)

    print("=" * 60)
    print("Seed Faker completado")
    print("=" * 60)
    print(f"Clientes creados: {created_clients}")
    print(f"Productos creados: {created_products}")
    print(f"Compras creadas: {created_purchases}")
    print(f"Ventas creadas: {created_sales}")
    print(f"Compania usada: {company.name}")
    print("Usuarios base disponibles: superadmin/admin/vendedor/almacen")
    print("Contrasenas: superadmin123, admin123, vendedor123, almacen123")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera datos fake para el sistema")
    parser.add_argument("--locale", default="es_ES", help="Locale de Faker (default: es_ES)")
    parser.add_argument("--seed", type=int, default=20260409, help="Semilla aleatoria")
    parser.add_argument("--company", default="Porcelanatos Demo", help="Nombre del negocio de prueba")
    parser.add_argument("--clients", type=int, default=30, help="Cantidad de clientes a crear")
    parser.add_argument("--products", type=int, default=50, help="Cantidad de productos a crear")
    parser.add_argument("--purchases", type=int, default=20, help="Cantidad de compras a crear")
    parser.add_argument("--sales", type=int, default=35, help="Cantidad de ventas a crear")
    parser.add_argument("--sellers", type=int, default=4, help="Cantidad minima de vendedores activos")
    parser.add_argument("--max-items", type=int, default=5, help="Maximo de items por compra/venta")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
