from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ["id", "name", "code"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Products
        fields = ["id", "name", "detail", "description", "category", "image_url"]


class ProductDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductDetail
        fields = ["id", "price", "color_code", "color_name", "quantity", "product"]


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orders
        fields = ["id", "name", "phone", "address", "note"]


class CartSerializer(serializers.ModelSerializer):
    product_detail = ProductDetailSerializer()
    order = OrderSerializer()

    class Meta:
        model = Carts
        fields = ["id", "order", "product_detail", "quantity"]
