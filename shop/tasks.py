from datetime import timedelta
from django.utils.timezone import now
from .models import Notification

def delete_old_notifications():
    cutoff = now() - timedelta(days=7)
    Notification.objects.filter(created_at__lt=cutoff).delete()
