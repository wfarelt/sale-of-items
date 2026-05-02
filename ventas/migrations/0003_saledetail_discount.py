from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0002_alter_saledetail_quantity"),
    ]

    operations = [
        migrations.AddField(
            model_name="saledetail",
            name="discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[MinValueValidator(Decimal("0.00"))],
                verbose_name="Descuento",
            ),
        ),
    ]
