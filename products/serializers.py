from rest_framework import serializers

from ecommerce_backend.products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "active",
            "deleted",
        ]
