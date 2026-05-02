from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movimientos", "0002_alter_inventorymovement_quantity_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="inventorymovement",
            name="registered_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="inventory_movements",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Registrado por",
            ),
        ),
    ]
