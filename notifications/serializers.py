from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    unread = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "unread",
            "is_read",
            "created_at",
        ]

    def get_unread(self, obj):
        return not obj.is_read