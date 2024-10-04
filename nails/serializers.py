from rest_framework import serializers
from .models import *


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
    class Meta:
        model = Carts
        fields = ["product_detail", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    carts = CartSerializer(many=True)

    class Meta:
        model = Orders
        fields = [
            "name",
            "phone",
            "address",
            "note",
            "payment_method",
            "total_payment",
            "carts",
        ]

    def create(self, validated_data):
        carts_data = validated_data.pop("carts")
        order = Orders.objects.create(**validated_data)

        for cart_data in carts_data:
            Carts.objects.create(order=order, **cart_data)

        return order
