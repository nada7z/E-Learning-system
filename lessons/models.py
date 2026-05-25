from django.db import models
from accounts.models import User
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

from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )

    lesson = models.ForeignKey(
        "lessons.Lesson",
        on_delete=models.CASCADE,
        related_name="progress_records"
    )

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student} - {self.lesson} - {self.completed}"