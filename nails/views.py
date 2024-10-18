from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from . import *
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q

logger = logging.getLogger(__name__)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.create_user(
                    username=serializer.data["username"],
                    email=serializer.data["email"],
                    first_name=serializer.data["first_name"],
                    last_name=serializer.data["last_name"],
                    password=serializer.data["password"],
                )
                return Response(
                    {
                        "status": True,
                        "message": "Registration successfully",
                        "data": UserSerializer(user, many=False).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            errors = []
            fields_with_errors = []

            for field, field_errors in serializer.errors.items():
                fields_with_errors.append(field)
                errors.extend([str(error) for error in field_errors])

            return Response(
                {
                    "status": False,
                    "message": " ".join(errors),
                    "fields": fields_with_errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            data = serializer.data
            return Response(
                {"status": True, "message": "Success", "data": data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StandardPagesPagination(PageNumberPagination):
    page_size = 10


class CategoryView(APIView):
    def get(self, request):
        try:
            page_size = request.query_params.get("page_size")
            queryset = Categories.objects.all()

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

    def put(self, request, pk):
        try:
            category = Categories.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Categories.DoesNotExist:
            return Response(
                {"status": False, "message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            category = Categories.objects.get(pk=pk)
            data = CategorySerializer(category).data
            category.delete()
            return Response(
                {
                    "status": True,
                    "message": "Category deleted successfully.",
                    "data": data,
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Categories.DoesNotExist:
            return Response(
                {"status": False, "message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            product_id = request.query_params.get("product_id", None)
            search = request.query_params.get("search", None)
            queryset = Products.objects.all()
            if search:  # Kiểm tra nếu có giá trị tìm kiếm
                queryset = queryset.filter(Q(name__icontains=search))

            if product_id is not None:
                queryset = Products.objects.filter(id=product_id).order_by("id").first()
                serializer = ProductSerializer(queryset)
                return Response(
                    {"status": True, "message": "Sucess", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

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


class OrderView(APIView):
    def notify_admin_about_order(self, order):
        subject = "New Customer Order Notification"
        admin_email = "ducdoan1806@gmail.com"  # Your email address
        from_email = "ducdoan1806@gmail.com"

        # Render the order details into the email template
        serializer = OrderSerializer(order)

        total_price = sum(
            cart["price"] * cart["quantity"] for cart in serializer.data["carts"]
        )

        html_content = render_to_string(
            "email_template.html",
            {
                "order": serializer.data,
                "url": f"{FRONTEND_URL}/orders/{serializer.data['order_code']}",
                "store_name": "Gạo Nails",
                "total_price": total_price,
            },
        )
        # Create the email with both plain text and HTML content
        email = EmailMultiAlternatives(
            subject,
            "A customer has placed a new order.",  # Plain text version
            from_email,
            [admin_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    def get(self, request):
        try:
            page_size = int(request.query_params.get("page_size", 15))
            status = request.query_params.get("status")

            search_term = request.query_params.get("search")
            queryset = Orders.objects.all().order_by("-id")

            if status:
                queryset = queryset.filter(status=status)
            if search_term:  # Kiểm tra nếu có giá trị tìm kiếm
                queryset = queryset.filter(
                    Q(name__icontains=search_term)
                    | Q(order_code__icontains=search_term)
                )

            paginator = StandardPagesPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(queryset, request)

            serializer = OrderSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Orders.DoesNotExist:
            return Response(
                {"status": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": error_message(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            cart = request.data.get("carts")
            if len(cart) == 0:
                return Response(
                    {"status": False, "message": "Your cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = OrderSerializer(data=request.data)

            if serializer.is_valid():
                order = serializer.save()
                try:
                    self.notify_admin_about_order(order)
                except Exception as email_error:
                    # Log email sending error, but don't fail the response
                    print(f"Email error: {str(email_error)}")

                return Response(
                    {
                        "status": True,
                        "message": "Order created and admin notified",
                        "data": serializer.data,
                    },
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


class OrderDetailView(APIView):
    def get(self, request, pk):
        try:
            queryset = Orders.objects.get(order_code=pk)
            serializer = OrderSerializer(queryset)

            return Response(
                {"status": True, "message": "Success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Orders.DoesNotExist:
            return Response(
                {"status": False, "message": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, pk):
        try:
            order = Orders.objects.get(id=pk)
            new_status = request.data.get("status")

            if new_status:
                order.status = new_status
                order.save()
                serializer = OrderSerializer(order)
                return Response(
                    {
                        "status": True,
                        "message": "Order status updated successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": True, "error": "Status is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Orders.DoesNotExist:
            return Response(
                {"status": False, "message": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OverView(APIView):
    def get(self, request):
        try:
            order_count = Orders.objects.count()
            product_count = Products.objects.count()
            order_completed = Orders.objects.filter(status="COMPLETED")
            completed_order_count = order_completed.count()
            total_revenue = 0
            for order in order_completed:
                for cart in order.carts.all():
                    total_revenue += cart.price * cart.quantity
            orders = Orders.objects.filter(status="PENDING").order_by("-id")[:10]
            serializers = OrderSerializer(orders, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Success",
                    "data": {
                        "order_count": order_count,
                        "completed_order_count": completed_order_count,
                        "total_revenue": total_revenue,
                        "product_count": product_count,
                        "recent_order": serializers.data,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddressView(APIView):
    def get(self, request):
        try:
            city_code = request.query_params.get("city", None)
            district_code = request.query_params.get("district", None)
            if city_code:
                city = City.objects.get(code=city_code)
                district = District.objects.filter(city=city)
                return Response(
                    {
                        "status": True,
                        "message": "Success",
                        "data": DistrictSerializer(district, many=True).data,
                    },
                    status=status.HTTP_200_OK,
                )
            if district_code:
                district = District.objects.get(code=district_code)
                ward = Ward.objects.filter(district=district)
                return Response(
                    {
                        "status": True,
                        "message": "Success",
                        "data": WardSerializer(ward, many=True).data,
                    },
                    status=status.HTTP_200_OK,
                )
            city = City.objects.all()
            return Response(
                {
                    "status": True,
                    "message": "Success",
                    "data": CitySerializer(city, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except City.DoesNotExist:
            return Response(
                {"status": False, "message": "City not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except District.DoesNotExist:
            return Response(
                {"status": False, "message": "District not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": error_message(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
