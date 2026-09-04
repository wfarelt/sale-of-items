from decimal import Decimal

from django.db import migrations
from django.db.models import Sum


def reconcile_reserved_stock(apps, schema_editor):
	Product = apps.get_model("productos", "Product")
	SaleDetail = apps.get_model("ventas", "SaleDetail")

	Product.objects.update(stock_reservado=Decimal("0.00"))
	reserved_quantities = (
		SaleDetail.objects.filter(sale__status="reserved")
		.values("product_id")
		.annotate(quantity=Sum("quantity"))
	)
	for item in reserved_quantities:
		Product.objects.filter(pk=item["product_id"]).update(stock_reservado=item["quantity"])


class Migration(migrations.Migration):

	dependencies = [
		("ventas", "0005_update_sale_status_labels"),
	]

	operations = [
		migrations.RunPython(reconcile_reserved_stock, migrations.RunPython.noop),
	]