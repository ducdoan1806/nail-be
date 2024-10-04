from django.urls import path
from .views import *


urlpatterns = [
    path("categories/", CategoryView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryView.as_view(), name="category-detail"),
    path(
        "images/",
        ProductImageUploadView.as_view(),
        name="images",
    ),
    path(
        "images/<int:pk>/",
        ProductImageUploadView.as_view(),
        name="image-upload",
    ),
    path("products/", ProductView.as_view(), name="products-list"),
    path("products/<int:pk>/", ProductView.as_view(), name="products-detail"),
    path("product-detail/", ProductDetailView.as_view(), name="product-detail"),
    path("order/", OrderView.as_view(), name="order"),
]
