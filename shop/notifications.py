from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


def save_and_notify(user, message):
    Notification.objects.create(user=user, message=message)

    # 2. Send in real time
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.username}",
        {
            "type": "send_notification",
            "content": {"message": message},
        },
    )


def notify_order_created_to_admins(order):
    # Find all staff/admin users
    admin = User.objects.get(is_staff=True)
    save_and_notify(
        admin,
        f"New order {order.id} placed by {order.user.username} for '{order.product.name}'.",
    )


def notify_user_order_created(user, order):
    save_and_notify(
        user,
        f"Order {order.id} placed successfully for product '{order.product.name}'.",
    )


def notify_user_order_status_changed(user, order):
    save_and_notify(user, f"Order {order.id} status updated to '{order.status}'.")


def notify_user_cart_updated(user, cart_item):
    save_and_notify(
        user,
        f"'{cart_item.productId.name}' added to your cart. Quantity: {cart_item.quantity}.",
    )
