from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    image = models.URLField()
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name
