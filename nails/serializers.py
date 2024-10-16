from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "id",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ["id", "name", "code"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "created_at"]


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDetail
        fields = ["id", "price", "color_code", "color_name", "quantity"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    mini_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    detail_products = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "detail",
            "description",
            "mini_price",
            "category",
            "images",
            "detail_products",
        ]

    def get_detail_products(self, product_id):
        product_detail = ProductDetail.objects.filter(product_id=product_id)
        return ProductDetailSerializer(product_detail, many=True).data

    def get_mini_price(self, product_id):
        product_detail = ProductDetail.objects.filter(product_id=product_id)
        min_prc = None
        for details in product_detail:
            if min_prc is None or details.price < min_prc:
                min_prc = details.price
        return min_prc


class CartSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    detail = serializers.SerializerMethodField(read_only=True)

    def get_products(self, data):
        try:
            return ProductSerializer(data.product_detail.product, many=False).data
        except Exception as e:
            print(f"{e}")
            return None

    def get_detail(self, data):
        return ProductDetailSerializer(data.product_detail, many=False).data

    class Meta:
        model = Carts
        fields = ["product_detail", "detail", "products", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    carts = CartSerializer(many=True)

    class Meta:
        model = Orders
        fields = [
            "id",
            "name",
            "phone",
            "address",
            "note",
            "payment_method",
            "city_code",
            "district_code",
            "ward_code",
            "serial_number",
            "order_code",
            "status",
            "created_at",
            "carts",
        ]

    def create(self, validated_data):
        carts_data = validated_data.pop("carts")
        order = Orders.objects.create(**validated_data)
        for cart_data in carts_data:
            Carts.objects.create(order=order, **cart_data)

        return order
