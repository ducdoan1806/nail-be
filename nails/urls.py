from django.urls import path, include
from .views import *
from rest_framework import routers


urlpatterns = [
    path("categories/", CategoryView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryView.as_view(), name="category-detail"),
    path(
        "images/<int:product_id>/",
        ProductImageUploadView.as_view(),
        name="image-upload",
    ),
    path("products/", ProductView.as_view(), name="products-list"),
    path("products/<int:pk>/", ProductView.as_view(), name="products-detail"),
]
