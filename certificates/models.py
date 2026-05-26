from django.db import models
from accounts.models import Student
from courses.models import Course


class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    certificate_code = models.CharField(max_length=255, unique=True)

    pdf_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return self.certificate_code