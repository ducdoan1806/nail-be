from django.db import models


# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Products(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    detail = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductDetail(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    price = models.IntegerField()
    color_code = models.CharField(max_length=100)
    color_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.color_name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Products, related_name="images", on_delete=models.DO_NOTHING
    )
    image = models.ImageField(upload_to="uploads/images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Orders(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)

    payment_method = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Carts(models.Model):
    product_detail = models.ForeignKey(ProductDetail, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Orders, related_name="carts", on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart: {self.product_detail} (Quantity: {self.quantity})"
