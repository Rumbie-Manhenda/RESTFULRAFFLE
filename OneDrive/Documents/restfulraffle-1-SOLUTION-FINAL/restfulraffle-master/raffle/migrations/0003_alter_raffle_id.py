# Generated by Django 4.2.1 on 2024-08-09 17:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0002_alter_ticket_unique_together_raffle_prizes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="raffle",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
