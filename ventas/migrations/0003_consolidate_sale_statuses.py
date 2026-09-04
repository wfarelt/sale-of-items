from django.db import migrations, models


def consolidate_sale_statuses(apps, schema_editor):
	Sale = apps.get_model("ventas", "Sale")

	Sale.objects.filter(status="draft").update(status="proforma")
	Sale.objects.filter(status__in=["anulada", "canceled"]).update(status="cancelled")
	Sale.objects.filter(status="delivered").update(status="confirmed")
	Sale.objects.filter(status="confirmada", delivered_at__isnull=True).update(
		status="confirmed",
		delivered_at=models.F("date"),
	)
	Sale.objects.filter(status="confirmada").update(status="confirmed")


class Migration(migrations.Migration):

	dependencies = [
		("ventas", "0002_unify_sale_status_values"),
	]

	operations = [
		migrations.RunPython(consolidate_sale_statuses, migrations.RunPython.noop),
		migrations.AlterField(
			model_name="sale",
			name="status",
			field=models.CharField(
				choices=[
					("proforma", "Proforma"),
					("reserved", "Reservada"),
					("ordered", "Pedido"),
					("confirmed", "Confirmada"),
					("cancelled", "Cancelada"),
				],
				default="proforma",
				max_length=20,
				verbose_name="Estado",
			),
		),
	]