# Generated by Django 4.2.20 on 2025-06-26 04:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_product_unit_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='ordered_by',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
