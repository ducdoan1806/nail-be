from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from . import *
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Q
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import AllowAny, IsAuthenticated

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
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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
        try:
            logger.info("Creating a new category")
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Category is created",
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

    def put(self, request, pk):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            category = Categories.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Category is updated",
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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            category = Categories.objects.get(pk=pk)
            data = CategorySerializer(category).data
            category.delete()
            return Response(
                {
                    "status": True,
                    "message": "Category is deleted.",
                    "data": data,
                },
                status=status.HTTP_200_OK,
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
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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

    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            product_id = request.data.get("product_id")
            product = Products.objects.get(id=product_id)
            images = request.FILES.getlist("images")
            uploaded_image_urls = []
            for image in images:
                img_instance = ProductImage.objects.create(product=product, image=image)
                uploaded_image_urls.append(
                    {
                        "id": img_instance.id,
                        "image": img_instance.image.url,
                        "created_at": img_instance.created_at,
                    }
                )
            return Response(
                {
                    "status": True,
                    "message": "Image is uploaded",
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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            image = ProductImage.objects.get(pk=pk)
            image_data = ProductImageSerializer(image).data

            if image.image:
                if os.path.isfile(image.image.path):
                    os.remove(image.image.path)

            image.delete()

            return Response(
                {
                    "status": True,
                    "message": "Image is deleted",
                    "data": image_data,
                },
                status=status.HTTP_200_OK,
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
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
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
                {
                    "status": True,
                    "message": "Product is created",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            product = Products.objects.get(id=pk)
            category_id = request.data.get("category")
            category = Categories.objects.get(id=category_id)
            request.data["category"] = category.id

            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Product updated successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Products.DoesNotExist:
            return Response(
                {"status": False, "message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Categories.DoesNotExist:
            return Response(
                {"status": False, "message": "Category not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            product = Products.objects.get(pk=pk)
            data = ProductSerializer(product).data
            product.delete()
            return Response(
                {
                    "status": True,
                    "message": "Product is deleted.",
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )
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


class ProductDetailView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
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
                {
                    "status": True,
                    "message": "Product detail is created",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            product_detail = ProductDetail.objects.get(id=pk)
            serializer = ProductDetailSerializer(product_detail, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Product variant is updated",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ProductDetail.DoesNotExist:
            return Response(
                {"status": False, "message": "Product variant not found."},
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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            product_variant = ProductDetail.objects.get(pk=pk)
            data = ProductDetailSerializer(product_variant).data
            product_variant.delete()
            return Response(
                {
                    "status": True,
                    "message": "Product variant is deleted.",
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )
        except ProductDetail.DoesNotExist:
            return Response(
                {"status": False, "message": "Product variant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            page_size = int(request.query_params.get("page_size", 15))
            status_order = request.query_params.get("status")
            search_term = request.query_params.get("search")
            queryset = Orders.objects.all().order_by("-id")

            if status_order:
                queryset = queryset.filter(status=status_order)
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
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

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
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
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
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [AllowAny]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"status": False, "message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
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


class HeroAPIView(APIView):

    # GET all heroes
    def get(self, request):
        try:
            heroes = Hero.objects.all()
            serializer = HeroSerializer(heroes, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Successful",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # POST a new hero
    def post(self, request):
        try:
            serializer = HeroSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": False,
                        "message": "Hero is created",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {
                    "status": False,
                    "message": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HeroDetailAPIView(APIView):

    # GET a single hero
    def get(self, request, pk):
        try:
            hero = Hero.objects.get(pk)
            serializer = HeroSerializer(hero)
            return Response(
                {
                    "status": True,
                    "message": "Successful",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Hero.DoesNotExist:
            return Response(
                {"status": False, "message": "Hero not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # PUT to update a hero
    def put(self, request, pk):
        try:
            hero = Hero.objects.get(pk)
            serializer = HeroSerializer(hero, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Successful",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": False,
                    "message": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Hero.DoesNotExist:
            return Response(
                {"status": False, "message": "Hero not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # DELETE a hero
    def delete(self, request, pk):
        try:
            hero = Hero.objects.get(pk)
            serializer = HeroSerializer(hero)
            hero.delete()
            return Response(
                {"status": True, "message": "Successful", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Hero.DoesNotExist:
            return Response(
                {"status": False, "message": "Hero not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = error_message(e)
            return Response(
                {"status": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagesPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
