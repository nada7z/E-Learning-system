from django.db import models
from courses.models import Course


class Lesson(models.Model):
    LESSON_TYPES = [
        ("video", "Video"),
        ("reading", "Reading"),
        ("quiz", "Quiz"),
        ("assignment", "Assignment"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=255)

    content = models.TextField(blank=True)

    # External video link
    video_url = models.URLField(blank=True, null=True)

    # Uploaded video file
    video_file = models.FileField(
        upload_to="lesson_videos/",
        blank=True,
        null=True
    )

    lesson_type = models.CharField(
        max_length=50,
        choices=LESSON_TYPES,
        default="reading"
    )

    order_number = models.PositiveIntegerField(default=1)

    is_preview = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_number"]

    def __str__(self):
        return self.title