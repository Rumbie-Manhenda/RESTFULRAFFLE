# Generated by Django 4.2.1 on 2024-08-12 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0007_alter_raffle_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="verification_code",
            field=models.CharField(editable=False, max_length=128, unique=True),
        ),
    ]
