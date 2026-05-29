from django.db import migrations, models


def normalize_sale_statuses(apps, schema_editor):
    Sale = apps.get_model("ventas", "Sale")

    status_map = {
        "draft": "proforma",
        "canceled": "cancelled",
    }

    for old_value, new_value in status_map.items():
        Sale.objects.filter(status=old_value).update(status=new_value)


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(normalize_sale_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sale",
            name="status",
            field=models.CharField(
                choices=[
                    ("proforma", "Proforma"),
                    ("reserved", "Reservada"),
                    ("ordered", "Pedido"),
                    ("confirmed", "CONFIRMED - Venta aceptada"),
                    ("delivered", "DELIVERED - Entregado"),
                    ("cancelled", "CANCELLED - Cancelado"),
                    ("confirmada", "Confirmada"),
                    ("anulada", "Anulada"),
                ],
                default="confirmada",
                max_length=20,
                verbose_name="Estado",
            ),
        ),
    ]
