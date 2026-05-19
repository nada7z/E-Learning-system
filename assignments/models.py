from django.db import models
from courses.models import Course
from accounts.models import Student


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    text_answer = models.TextField(blank=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.assignment}"