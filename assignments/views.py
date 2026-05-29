from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from courses.models import Enrollment, Course
from notifications.utils import create_notification
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

        if hasattr(user, "teacher_profile"):
            return Assignment.objects.filter(
                course__teacher=user.teacher_profile
            ).order_by("-created_at")

        if hasattr(user, "student_profile"):
            enrolled_courses = Enrollment.objects.filter(
                student=user.student_profile
            ).values_list("course_id", flat=True)

            return Assignment.objects.filter(
                course_id__in=enrolled_courses
            ).order_by("-created_at")

        if getattr(user, "role", None) == "admin":
            return Assignment.objects.all().order_by("-created_at")

        return Assignment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can create assignments.")

        course_id = (
            self.request.data.get("course")
            or self.request.data.get("course_id")
            or self.request.query_params.get("course")
            or self.request.query_params.get("course_id")
        )

        if not course_id:
            raise PermissionDenied("Course is required.")

        try:
            course = Course.objects.get(
                id=course_id,
                teacher=user.teacher_profile
            )
        except Course.DoesNotExist:
            raise PermissionDenied("You can only create assignments for your own courses.")

        serializer.save(course=course)

    def perform_update(self, serializer):
        user = self.request.user
        assignment = self.get_object()

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can edit assignments.")

        if assignment.course.teacher != user.teacher_profile:
            raise PermissionDenied("You can only edit assignments from your own courses.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can delete assignments.")

        if instance.course.teacher != user.teacher_profile:
            raise PermissionDenied("You can only delete assignments from your own courses.")

        instance.delete()

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "student_profile"):
            return Submission.objects.filter(
                student=user.student_profile
            ).order_by("-submitted_at")

        if hasattr(user, "teacher_profile"):
            return Submission.objects.filter(
                assignment__course__teacher=user.teacher_profile
            ).order_by("-submitted_at")

        if getattr(user, "role", None) == "admin":
            return Submission.objects.all().order_by("-submitted_at")

        return Submission.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "student_profile"):
            raise PermissionDenied("Only students can submit assignments.")

        assignment = serializer.validated_data["assignment"]

        if Submission.objects.filter(
            assignment=assignment,
            student=user.student_profile
        ).exists():
            raise PermissionDenied("You already submitted this assignment.")

        serializer.save(student=user.student_profile)

        submission = serializer.save(student=user.student_profile)

        teacher_user = submission.assignment.course.teacher.user

        create_notification(
            teacher_user,
            "New assignment submission",
            f"{user.student_profile} submitted {submission.assignment.title}."
        )

    def perform_update(self, serializer):
        user = self.request.user
        submission = self.get_object()

        if hasattr(user, "teacher_profile"):
            if submission.assignment.course.teacher != user.teacher_profile:
                raise PermissionDenied(
                    "You can only grade submissions from your own courses."
                )

            submission = serializer.save()

            create_notification(
                submission.student.user,
                "Assignment graded",
                f"Your assignment {submission.assignment.title} has been graded."
            )
            return

        raise PermissionDenied("Only teachers can update submissions.")