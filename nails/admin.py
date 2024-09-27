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
        "image_url",
        "description",
        "category",
        "created_at",
        "updated_at",
    )


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductDetail)
admin.site.register(Orders)
admin.site.register(Carts)
