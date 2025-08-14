from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, CustomLoginView,
                    ForgotPasswordView, OrderViewSet, ResetPasswordView, UserRegisterView, WishlistViewSet,
                    create_razorpay_order, verify_payment, NotificationViewSet)
from ..products.views import ProductViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"catogories", CategoryViewSet)
router.register(r"cart", CartViewSet)
router.register(r"wishlist", WishlistViewSet)
router.register(r"order", OrderViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
urlpatterns = [
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("register/<int:pk>/", UserRegisterView.as_view(), name="register_pk"),
    path("login/", CustomLoginView.as_view(), name="custom_login"),
    path("create-order/", create_razorpay_order),
    path("verify-payment/", verify_payment),
    path("", include(router.urls)),
]
