from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from . import *
import logging

logger = logging.getLogger(__name__)


class StandardPagesPagination(PageNumberPagination):
    page_size = 10


class CategoryView(APIView):
    def get(self, request):
        try:

            page_size = request.query_params.get("page_size")
            queryset = Categories.objects.all().order_by("id")

            paginator = StandardPagesPagination()
            paginator.page_size = int(page_size) if page_size is not None else 15

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = CategorySerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        logger.info("Creating a new category")
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Category created",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProductImageUploadView(APIView):
    def get(self, request):
        try:
            page_size = request.query_params.get("page_size")
            product = request.query_params.get("product_id")
            if product is not None:
                queryset = ProductImage.objects.filter(product_id=product).order_by(
                    "id"
                )
            else:
                queryset = ProductImage.objects.all().order_by("id")
            paginator = StandardPagesPagination()
            paginator.page_size = int(page_size) if page_size is not None else 15

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ProductImageSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, pk):
        try:
            product = Products.objects.get(id=pk)
            images = request.FILES.getlist("images")
            uploaded_image_urls = []
            for image in images:
                img_instance = ProductImage.objects.create(product=product, image=image)
                uploaded_image_urls.append(img_instance.image.url)
            return Response(
                {
                    "status": True,
                    "message": "Success",
                    "data": {"product_id": product.id, "images": uploaded_image_urls},
                },
                status=status.HTTP_201_CREATED,
            )
        except Products.DoesNotExist:
            return Response(
                {"status": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": error_message(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk=None):
        try:
            image = ProductImage.objects.get(pk=pk)
            image_data = ProductImageSerializer(image).data

            if image.image:
                if os.path.isfile(image.image.path):
                    os.remove(image.image.path)

            image.delete()

            return Response(
                {
                    "status": True,
                    "message": "Image deleted",
                    "data": image_data,
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductImage.DoesNotExist:
            return Response(
                {"status": False, "message": "Image not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            logger.error(message)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductView(APIView):
    def get(self, request):
        try:
            page_size = request.query_params.get("page_size")
            product_id = request.query_params.get("product_id")

            if product_id is not None:
                queryset = Products.objects.filter(id=product_id).order_by("id").first()
                serializer = ProductSerializer(queryset)
                return Response(
                    {"status": True, "message": "Sucess", "data": serializer.data},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            queryset = Products.objects.all().order_by("id")
            paginator = StandardPagesPagination()
            paginator.page_size = int(page_size) if page_size is not None else 15

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Products.DoesNotExist:
            return Response(
                {"status": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            name = request.data.get("name")
            category_id = request.data.get("category")
            detail = request.data.get("detail")
            description = request.data.get("description")

            category = Categories.objects.get(id=category_id)
            product = Products.objects.create(
                name=name, category=category, detail=detail, description=description
            )

            serializer = ProductSerializer(product)

            return Response(
                {"status": True, "message": "Success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductDetailView(APIView):
    def get(self, request):
        try:
            page_size = request.query_params.get("page_size")
            product_id = request.query_params.get("product_id")
            if product_id is not None:
                queryset = ProductDetail.objects.filter(product_id=product_id).order_by(
                    "id"
                )
            else:
                queryset = ProductDetail.objects.all().order_by("id")
            paginator = StandardPagesPagination()
            paginator.page_size = int(page_size) if page_size is not None else 15

            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ProductDetailSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            product = request.data.get("product")
            price = request.data.get("price")
            color_code = request.data.get("color_code")
            color_name = request.data.get("color_name")
            quantity = request.data.get("quantity")

            product = Products.objects.get(id=product)
            product_detail = ProductDetail.objects.create(
                price=price,
                color_code=color_code,
                color_name=color_name,
                quantity=quantity,
                product=product,
            )

            serializer = ProductDetailSerializer(product_detail)

            return Response(
                {"status": True, "message": "Success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
