from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from courses.models import Enrollment
from .models import Assignment, Submission
from .serializers import (
    AssignmentSerializer,
    SubmissionSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Teacher
        if hasattr(user, "teacher_profile"):
            return Assignment.objects.filter(
                course__teacher=user.teacher_profile
            ).order_by("-created_at")

        # Student
        if hasattr(user, "student_profile"):
            enrolled_courses = Enrollment.objects.filter(
                student=user.student_profile
            ).values_list("course_id", flat=True)

            return Assignment.objects.filter(
                course_id__in=enrolled_courses
            ).order_by("-created_at")

        # Admin
        if getattr(user, "role", None) == "admin":
            return Assignment.objects.all().order_by("-created_at")

        return Assignment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can create assignments."
            )

        course = serializer.validated_data.get("course")

        if course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only create assignments for your own courses."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        assignment = self.get_object()

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can edit assignments."
            )

        if assignment.course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only edit assignments from your own courses."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can delete assignments."
            )

        if instance.course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only delete assignments from your own courses."
            )

        instance.delete()


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Student
        if hasattr(user, "student_profile"):
            return Submission.objects.filter(
                student=user.student_profile
            ).order_by("-submitted_at")

        # Teacher
        if hasattr(user, "teacher_profile"):
            return Submission.objects.filter(
                assignment__course__teacher=user.teacher_profile
            ).order_by("-submitted_at")

        # Admin
        if getattr(user, "role", None) == "admin":
            return Submission.objects.all().order_by("-submitted_at")

        return Submission.objects.none()

    def perform_create(self, serializer):
        serializer.save(
            student=self.request.user.student_profile
        )