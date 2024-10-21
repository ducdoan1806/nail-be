from django.urls import path
from .views import *


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("oauth2-info/", AuthInfo.as_view()),
    path("user/", UserView.as_view(), name="user"),
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
    # path("products/<int:pk>/", ProductView.as_view(), name="products-detail"),
    path("product-detail/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "product-detail/<int:pk>/", ProductDetailView.as_view(), name="products-detail"
    ),
    path("order/", OrderView.as_view(), name="order"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("overview/", OverView.as_view(), name="overview"),
    path("address/", AddressView.as_view(), name="address"),
]
