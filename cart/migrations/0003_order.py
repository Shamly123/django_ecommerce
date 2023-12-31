# Generated by Django 4.2.1 on 2023-08-23 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0005_alter_profile_profile_image"),
        ("cart", "0002_alter_cartitem_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                ("order_number", models.CharField(max_length=20)),
                ("subtotal", models.IntegerField(default=0)),
                (
                    "order_total",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Order placed", "Order placed"),
                            ("Shipped", "Shipped"),
                            ("Delivered", "Delivered"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Order Pending",
                        max_length=15,
                    ),
                ),
                ("is_orderd", models.BooleanField(default=False)),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.address",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
