from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="proforma_validity_days",
            field=models.PositiveIntegerField(default=7, verbose_name="Dias de validez de proforma"),
        ),
        migrations.AddField(
            model_name="company",
            name="utility_margin_percent",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("35.00"),
                max_digits=5,
                validators=[MinValueValidator(Decimal("0.00"))],
                verbose_name="Margen de utilidad (%)",
            ),
        ),
    ]
