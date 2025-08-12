import uuid
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from .models import Cart, Category, Order, Product, User, Wishlist,Notification
from .notifications import (notify_user_cart_updated,
                            notify_user_order_created,
                            notify_user_order_status_changed,
                            notify_order_created_to_admins)
from .serializers import (CartSerializer, CategorySerializer,
                          CustomTokenObtainPairSerializer, OrderSerializer,
                          ProductSerializer, UserSerializer,
                          WishlistSerializer,NotificationSerializer)

reset_tokens = {}  # Temporary store (use DB for production)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            token = get_random_string(32)
            reset_tokens[token] = user.username

            reset_link = f"http://localhost:5173/reset-password?token={token}"
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return Response(
                {"message": "Password reset email sent"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        if token in reset_tokens:
            username = reset_tokens[token]
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            del reset_tokens[token]
            return Response(
                {"message": "Password reset successful"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST
        )


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@api_view(["POST"])
def create_razorpay_order(request):
    amount = request.data.get("amount")
    if not amount:
        return Response(
            {"status": "error", "message": "Amount is required"}, status=400
        )

    amount_in_paise = int(amount) * 100
    order_receipt = str(uuid.uuid4())[:12]

    razorpay_order = client.order.create(
        {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": order_receipt,
            "payment_capture": "1",
        }
    )

    return Response(
        {
            "status": "success",
            "order_id": razorpay_order["id"],
            "amount": amount_in_paise,
            "currency": "INR",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        },
        status=200,
    )


@api_view(["POST"])
def verify_payment(request):
    data = request.data

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": data.get("razorpay_order_id"),
                "razorpay_payment_id": data.get("razorpay_payment_id"),
                "razorpay_signature": data.get("razorpay_signature"),
            }
        )
        return Response(
            {"status": "success", "message": "Payment Verified Successfully"},
            status=200,
        )

    except razorpay.errors.SignatureVerificationError:
        return Response(
            {"status": "error", "message": "Payment verification failed"}, status=400
        )


class UserRegisterView(APIView):
    permission_map = {
        "POST": [AllowAny],
        "PATCH": [AllowAny],
        "GET": [AllowAny],
    }

    def get_permissions(self):
        return [perm() for perm in self.permission_map.get(self.request.method, self.permission_classes)]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Let DRF handle errors
        serializer.save()
        return Response(
            {
                "status": "success",
                "message": "User registered successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk, is_superuser=False)
            serializer = UserSerializer(user)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        queryset = User.objects.filter(is_superuser=False).order_by("id")
        serializer = UserSerializer(queryset, many=True)

        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_superuser=False)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # No need for manual 400
        serializer.save()
        return Response(
            {"status": "success", "message": "User updated", "data": serializer.data},
            status=status.HTTP_200_OK
        )


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "category__name",
    ]
    permission_classes = [AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.select_related(
        "userId", "productId", "productId__category"
    ).all()
    serializer_class = CartSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["userId", "productId"]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("userId")
        product_id = request.data.get("productId")
        quantity = int(request.data.get("quantity", 1))

        # Check if the item is already in cart
        cart_item = Cart.objects.filter(userId=user_id, productId=product_id).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()

            notify_user_cart_updated(cart_item.userId, cart_item)

            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new cart item
        new_cart_item = Cart.objects.create(
            userId_id=user_id, productId_id=product_id, quantity=quantity
        )

        # Notify user about cart addition
        notify_user_cart_updated(new_cart_item.userId, new_cart_item)

        serializer = self.get_serializer(new_cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Wishlist.objects.select_related(
        "userId", "productId", "productId__category"
    ).all()
    serializer_class = WishlistSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["userId", "productId"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.select_related(
            "userId", "productId", "productId__category"
        )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "product", "status"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return Response(
                {"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Reduce stock
        product.stock -= quantity
        product.save()

        # Save order via DRF
        response = super().create(request, *args, **kwargs)

        # Send notification
        if response.status_code == 201:
            order_instance = Order.objects.get(id=response.data["id"])
            notify_user_order_created(order_instance.user, order_instance)
            notify_order_created_to_admins(order_instance)

        return response

    def perform_update(self, serializer):
        old_order = Order.objects.get(id=serializer.instance.id)
        new_order = serializer.save()

        if old_order.status != new_order.status:
            notify_user_order_status_changed(new_order.user, new_order)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return Notification.objects.filter(user_id=user_id).order_by('-created_at')
        return Notification.objects.none()  # No ID, no notifications

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        user_id = self.request.query_params.get("user_id")
        deleted_count, _ = Notification.objects.filter(user_id=user_id).delete()
        return Response(
            {"message": f"Deleted {deleted_count} notifications."},
            status=status.HTTP_200_OK
        )
