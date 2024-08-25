# Generated by Django 4.2.1 on 2024-08-11 18:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0005_alter_ticket_ticket_number"),
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
