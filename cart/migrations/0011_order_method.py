# Generated by Django 4.2.1 on 2023-09-03 09:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cart", "0010_payment_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="method",
            field=models.CharField(default="cod", max_length=50),
            preserve_default=False,
        ),
    ]
