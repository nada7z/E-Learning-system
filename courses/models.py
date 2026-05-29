# courses/models.py

from django.db import models
from accounts.models import Teacher, Student


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)

    thumbnail = models.ImageField(upload_to="courses/", blank=True, null=True)

    level = models.CharField(
        max_length=50,
        choices=LEVEL_CHOICES,
        default="beginner"
    )

    language = models.CharField(max_length=100, default="English")

    duration_hours = models.PositiveIntegerField(default=0)

    has_certificate = models.BooleanField(default=False)

    tags = models.JSONField(default=list, blank=True)

    is_free = models.BooleanField(default=True)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} - {self.course}"
    
class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} - {self.course} - {self.status}"

class CourseReview(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.course} - {self.rating}/5"

class CourseDiscussion(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="discussions"
    )

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} - {self.course}"
    
