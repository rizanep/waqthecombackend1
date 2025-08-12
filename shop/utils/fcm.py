from firebase_admin import messaging
from ..models import FCMDevice

def send_push_notification(user, title, body):
    tokens = FCMDevice.objects.filter(user=user).values_list("registration_token", flat=True)

    if not tokens:
        return "No tokens found."

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=list(tokens),
    )

    response = messaging.send_multicast(message)
    return {
        "success": response.success_count,
        "failure": response.failure_count,
    }
