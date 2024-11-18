from django.db import models


class Hero(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contact(models.Model):
    SOCIAL_CHOICES = [
        ("Facebook", "Facebook"),
        ("Tiktok", "Tiktok"),
        ("Instagram", "Instagram"),
        ("Phone", "Phone"),
        ("Location", "Location"),
    ]
    social = models.CharField(max_length=50, choices=SOCIAL_CHOICES)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} ({self.social})"


class City(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField(unique=True)


class District(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField(unique=True)
    city = models.ForeignKey(City, related_name="districts", on_delete=models.CASCADE)


class Ward(models.Model):
    name = models.CharField(max_length=255)
    code = models.IntegerField(unique=True)
    district = models.ForeignKey(
        District, related_name="wards", on_delete=models.CASCADE
    )


class Categories(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.id) + " - " + self.name


class Products(models.Model):
    category = models.ForeignKey(Categories, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    detail = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.id) + " - " + self.name


class ProductDetail(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    price = models.IntegerField()
    color_code = models.CharField(max_length=100)
    color_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.id) + " - " + self.color_name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Products, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="uploads/images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Orders(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    payment_method = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city_code = models.CharField(max_length=10, null=True, blank=True)
    district_code = models.CharField(max_length=10, null=True, blank=True)
    ward_code = models.CharField(max_length=10, null=True, blank=True)
    serial_number = models.IntegerField(default=0)
    order_code = models.CharField(max_length=30, unique=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if self.serial_number == 0:  # Nếu serial_number chưa được đặt
            last_order = (
                Orders.objects.filter(
                    city_code=self.city_code,
                    district_code=self.district_code,
                    ward_code=self.ward_code,
                )
                .order_by("serial_number")
                .last()
            )

            if last_order:
                self.serial_number = last_order.serial_number + 1
            else:
                self.serial_number = 1  # Bắt đầu từ 1 nếu không có đơn hàng nào

        # Đảm bảo serial_number có 6 chữ số
        self.serial_number = str(self.serial_number).zfill(4)

        # Tạo order_code
        self.order_code = (
            f"{self.city_code}{self.district_code}{self.ward_code}{self.serial_number}"
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order: {self.order_code}"


class Carts(models.Model):
    product_detail = models.ForeignKey(ProductDetail, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Orders, related_name="carts", on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Cart: {self.product_detail} (Quantity: {self.quantity})"
