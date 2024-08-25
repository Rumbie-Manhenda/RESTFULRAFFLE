# Generated by Django 4.2.1 on 2024-08-12 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0008_alter_ticket_verification_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="raffle",
            name="name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("raffle", "ticket_number"), ("raffle", "participant_ip")},
        ),
    ]
