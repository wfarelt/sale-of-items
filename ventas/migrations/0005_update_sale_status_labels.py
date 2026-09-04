from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("ventas", "0004_rename_confirmed_to_executed"),
	]

	operations = [
		migrations.AlterField(
			model_name="sale",
			name="status",
			field=models.CharField(
				choices=[
					("proforma", "Proforma"),
					("reserved", "Reserva"),
					("ordered", "Importación"),
					("executed", "Ejecutada"),
					("cancelled", "Anulada"),
				],
				default="proforma",
				max_length=20,
				verbose_name="Estado",
			),
		),
	]