from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.response import Response
from . import *


class StandardPagesPagination(PageNumberPagination):
    page_size = 10


class CategoryView(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardPagesPagination

    def list(self, request):
        try:
            qs_data = self.queryset
            page_size = request.query_params.get("page_size")
            self.pagination_class.page_size = (
                int(page_size) if page_size is not None else 15
            )
            page = self.paginate_queryset(qs_data)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs_data, many=True)
            return Response(
                {"status": True, "message": "Success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductView(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardPagesPagination

    def create(self, request):
        try:

            name = request.data.get("name")
            category_id = request.data.get("category")
            image_url = request.data.get("image_url")
            category = Categories.objects.get(id=category_id)
            product = Products.objects.create(
                name=name, category=category, image_url=image_url
            )
            serializer = self.get_serializer(product)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "message": "Success", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
