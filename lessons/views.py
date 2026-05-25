from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from courses.models import Enrollment
from .models import Lesson, LessonProgress
from .serializers import LessonSerializer


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Teacher sees lessons from their own courses
        if hasattr(user, "teacher_profile"):
            return Lesson.objects.filter(
                course__teacher=user.teacher_profile
            ).order_by("order_number", "id")

        # Student sees lessons ONLY from enrolled courses
        if hasattr(user, "student_profile"):
            enrolled_courses = Enrollment.objects.filter(
                student=user.student_profile
            ).values_list("course_id", flat=True)

            return Lesson.objects.filter(
                course_id__in=enrolled_courses
            ).order_by("order_number", "id")

        # Admin sees everything
        if getattr(user, "role", None) == "admin":
            return Lesson.objects.all().order_by("order_number", "id")

        return Lesson.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can create lessons.")

        course = serializer.validated_data.get("course")

        if course.teacher != user.teacher_profile:
            raise PermissionDenied("You can only add lessons to your own courses.")

        serializer.save()

    @action(detail=True, methods=["post"])
    def toggle_complete(self, request, pk=None):
        lesson = self.get_object()
        user = request.user

        if not hasattr(user, "student_profile"):
            return Response(
                {"detail": "Only students can complete lessons."},
                status=status.HTTP_403_FORBIDDEN
            )

        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=user,
            lesson=lesson
        )

        lesson_progress.completed = not lesson_progress.completed
        lesson_progress.save()

        course = lesson.course

        total_lessons = Lesson.objects.filter(
            course=course
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            student=user,
            lesson__course=course,
            completed=True
        ).count()

        course_progress = 0

        if total_lessons > 0:
            course_progress = round(
                (completed_lessons / total_lessons) * 100
            )

        return Response({
            "course_id": course.id,
            "lesson_id": lesson.id,
            "lesson_completed": lesson_progress.completed,
            "course_progress": course_progress,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
        })