from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):

    video_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "title",
            "content",
            "video_url",
            "video_file",
            "video_file_url",
            "lesson_type",
            "order_number",
            "is_preview",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def get_video_file_url(self, obj):
        request = self.context.get("request")

        if obj.video_file and request:
            return request.build_absolute_uri(
                obj.video_file.url
            )

        return None