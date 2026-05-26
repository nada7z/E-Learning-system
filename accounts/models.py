from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        default='student'
    )

    email = models.EmailField(_('email address'), unique=True)   # Make email unique

    # Remove username if you want email-based login (optional but recommended)
    # username = None

    USERNAME_FIELD = 'email'          # Use email for login instead of username
    REQUIRED_FIELDS = ['username', 'role']   # Fields required when creating superuser

    def __str__(self):
        return f"{self.email} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.IntegerField(default=0)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"