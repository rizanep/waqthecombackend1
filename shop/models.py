from django.contrib.auth.models import AbstractUser
from django.db import models

from ecommerce_backend.products.models import Product


class User(AbstractUser):
    name = models.CharField(max_length=100)
    phn = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, default="user")
    blocked = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "username"  # or you can use email if you want login by email
    REQUIRED_FIELDS = [
        "email",
        "name",
        "phn",
    ]  # fields required when using createsuperuser

    def __str__(self):
        return self.username


class Cart(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cartuser")
    productId = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cartproduct"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("userId", "productId")


class Wishlist(models.Model):
    userId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlistuser"
    )
    productId = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlistproduct"
    )


class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Order Placed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="placed")


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"