# Generated by Django 4.2.1 on 2023-08-23 23:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cart", "0003_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Order placed", "Order placed"),
                    ("Shipped", "Shipped"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                default="Order Pending",
                max_length=15,
            ),
        ),
    ]
