# notifications/utils.py

from .models import Notification


def create_notification(user, title, message):
    if not user:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message
    )