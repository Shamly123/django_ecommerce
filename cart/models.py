from django.db import models
from product.models import Product
from accounts.models import Profile, Address
from base.models import BaseModel


# Create your models here.


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=50)
    couon_price = models.IntegerField()
    min_price = models.IntegerField()


class Cart(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    cart_id = models.CharField(max_length=100, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Cart"
        ordering = ["date_added"]

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartItem")
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "CartItem"

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product


class Order(BaseModel):
    status_choice = (
        ("Pending", "Pending"),
        ("Order placed", "Order placed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    )

    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="orders", blank=True, null=True
    )
    order_number = models.CharField(max_length=20)
    subtotal = models.IntegerField(default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(
        max_length=15, choices=status_choice, default="Order Pending"
    )
    is_orderd = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    coupon_price = models.BigIntegerField(default=0)
    offer = models.BigIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_item"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def total_price(self):
        return self.product.price * self.quantity
