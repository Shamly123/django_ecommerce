# Generated by Django 4.2.1 on 2023-08-15 05:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("house_name", models.CharField(max_length=150)),
                ("street", models.CharField(max_length=150)),
                ("pincode", models.IntegerField()),
                ("state", models.CharField(max_length=50)),
                ("city", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
