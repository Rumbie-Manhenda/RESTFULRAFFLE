# Generated by Django 4.2.1 on 2024-08-11 01:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0003_alter_raffle_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="ticket_number",
            field=models.BigIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
    ]
