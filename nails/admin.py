from django.contrib import admin
from .models import *


# Register your models here.
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "created_at", "updated_at")


class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "detail",
        "description",
        "category",
        "created_at",
        "updated_at",
    )


class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "color_code", "color_name", "quantity", "product")


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "created_at")


class OrdersAdmin(admin.ModelAdmin):
    list_display = (
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
    )


class CartsAdmin(admin.ModelAdmin):
    list_display = ("product_detail", "quantity", "price")


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductDetail, ProductDetailAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Carts, CartsAdmin)
