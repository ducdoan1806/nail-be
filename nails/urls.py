from django.urls import path, include
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register("categories", CategoryView, basename="categories")
router.register("products", ProductView, basename="products")
urlpatterns = [
    path("", include(router.urls)),
]
