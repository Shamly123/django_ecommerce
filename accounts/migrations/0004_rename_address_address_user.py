# Generated by Django 4.2.1 on 2023-08-15 06:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_address_address_address_alternate_number_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="address",
            old_name="address",
            new_name="user",
        ),
    ]
