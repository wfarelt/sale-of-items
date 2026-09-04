from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("ventas", "0003_consolidate_sale_statuses"),
	]

	operations = [
		migrations.RunSQL(
			"UPDATE ventas_sale SET status = 'executed' WHERE status = 'confirmed'",
			"UPDATE ventas_sale SET status = 'confirmed' WHERE status = 'executed'",
		),
		migrations.AlterField(
			model_name="sale",
			name="status",
			field=models.CharField(
				choices=[
					("proforma", "Proforma"),
					("reserved", "Reservada"),
					("ordered", "Pedido"),
					("executed", "Ejecutada"),
					("cancelled", "Cancelada"),
				],
				default="proforma",
				max_length=20,
				verbose_name="Estado",
			),
		),
	]