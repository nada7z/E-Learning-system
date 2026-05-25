from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Course, Enrollment
from .serializers import (
    CourseSerializer,
    CourseListSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, "teacher_profile"):
            return Course.objects.filter(teacher=user.teacher_profile).order_by("-created_at")

        if getattr(user, "role", None) == "admin":
            return Course.objects.all().order_by("-created_at")

        if getattr(user, "role", None) == "student":
            return Course.objects.filter(is_published=True).order_by("-created_at")

        return Course.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can create courses.")

        serializer.save(teacher=user.teacher_profile)

    def perform_update(self, serializer):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can update courses.")

        course = self.get_object()

        if course.teacher != user.teacher_profile:
            raise PermissionDenied("You can only update your own courses.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not hasattr(user, "teacher_profile"):
            raise PermissionDenied("Only teachers can delete courses.")

        if instance.teacher != user.teacher_profile:
            raise PermissionDenied("You can only delete your own courses.")

        instance.delete()

class PublishedCoursesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(
            is_published=True
        ).order_by("-created_at")

        serializer = CourseListSerializer(
            courses,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class EnrollCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):

        if not hasattr(request.user, "student_profile"):
            return Response(
                {
                    "detail":
                    "Only students can enroll."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            course = Course.objects.get(
                id=course_id,
                is_published=True
            )

        except Course.DoesNotExist:
            return Response(
                {
                    "detail":
                    "Course not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user.student_profile,
            course=course
        )

        if not created:
            return Response(
                {
                    "detail":
                    "Already enrolled."
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "detail":
                "Enrollment successful."
            },
            status=status.HTTP_201_CREATED
        )
    
def perform_update(self, serializer):
    user = self.request.user

    if not hasattr(user, "teacher_profile"):
        raise PermissionDenied("Only teachers can update courses.")

    course = self.get_object()

    if course.teacher != user.teacher_profile:
        raise PermissionDenied("You can only update your own courses.")

    serializer.save()


def perform_destroy(self, instance):
    user = self.request.user

    if not hasattr(user, "teacher_profile"):
        raise PermissionDenied("Only teachers can delete courses.")

    if instance.teacher != user.teacher_profile:
        raise PermissionDenied("You can only delete your own courses.")

    instance.delete()