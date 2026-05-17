from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "teacher_profile"):
            return Course.objects.filter(
                teacher=user.teacher_profile
            ).order_by("-created_at")

        if getattr(user, "role", None) == "admin":
            return Course.objects.all().order_by("-created_at")

        return Course.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can create courses.")

        serializer.save(teacher=user.teacher_profile)