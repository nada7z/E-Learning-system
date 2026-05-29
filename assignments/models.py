from django.db import models
from courses.models import Course
from accounts.models import Student


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    lesson = models.OneToOneField(
        "lessons.Lesson",
        on_delete=models.CASCADE,
        related_name="assignment",
        blank=True,
        null=True
    )

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

    class Meta:
        unique_together = ('assignment', 'student')

    @property
    def passed(self):
        if self.grade is None:
            return False

        return self.grade >= (self.assignment.max_score * 0.5)

    def __str__(self):
        return f"{self.student} - {self.assignment}"