from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from courses.models import Enrollment
from .models import Quiz, QuizAttempt
from .serializers import QuizSerializer, QuizAttemptSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "teacher_profile"):
            return Quiz.objects.filter(
                course__teacher=user.teacher_profile
            ).order_by("-created_at")

        if hasattr(user, "student_profile"):
            enrolled_courses = Enrollment.objects.filter(
                student=user.student_profile
            ).values_list("course_id", flat=True)

            return Quiz.objects.filter(
                course_id__in=enrolled_courses,
                is_published=True
            ).order_by("-created_at")

        if getattr(user, "role", None) == "admin":
            return Quiz.objects.all().order_by("-created_at")

        return Quiz.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can create quizzes."
            )

        course = serializer.validated_data.get("course")

        if course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only create quizzes for your own courses."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        quiz = self.get_object()

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can edit quizzes."
            )

        if quiz.course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only edit quizzes from your own courses."
            )

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied(
                "Only teachers can delete quizzes."
            )

        if instance.course.teacher != user.teacher_profile:
            raise PermissionDenied(
                "You can only delete quizzes from your own courses."
            )

        instance.delete()


class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "student_profile"):
            return QuizAttempt.objects.filter(
                student=user.student_profile
            ).order_by("-submitted_at")

        if hasattr(user, "teacher_profile"):
            return QuizAttempt.objects.filter(
                quiz__course__teacher=user.teacher_profile
            ).order_by("-submitted_at")

        if getattr(user, "role", None) == "admin":
            return QuizAttempt.objects.all().order_by("-submitted_at")

        return QuizAttempt.objects.none()