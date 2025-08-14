# serializers.py
import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Cart, Category, Order, Product, Wishlist,Notification


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user data to response
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "name": self.user.name,
            "phn": self.user.phn,
            "role": self.user.role,
            "blocked": self.user.blocked,
            "active": self.user.active,
            "is_admin": self.user.is_admin,
        }
        return data


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "phn",
            "email",
            "username",
            "password",
            "password2",
            "role",
            "blocked",
            "active",
            "is_admin",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        # Only validate passwords if they are provided (e.g., during create or password update)
        if password or password2:
            if not password:
                raise serializers.ValidationError(
                    {"password": "This field is required."}
                )
            if not password2:
                raise serializers.ValidationError(
                    {"password2": "This field is required."}
                )

            if len(password) < 8:
                raise serializers.ValidationError(
                    {"password": "Password must be at least 8 characters long."}
                )

            if not re.search(r"[A-Za-z]", password):
                raise serializers.ValidationError(
                    {
                        "password": "Password must contain at least one alphabetic character."
                    }
                )

            if not re.search(r"[0-9]", password):
                raise serializers.ValidationError(
                    {
                        "password": "Password must contain at least one numeric character."
                    }
                )

            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                raise serializers.ValidationError(
                    {
                        "password": "Password must contain at least one special character."
                    }
                )

            if password != password2:
                raise serializers.ValidationError({"Error": "Passwords do not match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=15, required=True)
    address_line = serializers.CharField(required=True)
    city = serializers.CharField(max_length=100, required=True)
    zip_code = serializers.CharField(max_length=10, required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = Order
        fields = "__all__"

    def validate_phone(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError(
                "Phone must be at least 10 digits and numeric."
            )
        return value

    def validate_zip_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Zip code must be numeric.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']