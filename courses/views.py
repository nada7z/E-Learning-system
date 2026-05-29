from urllib import request

from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response

from notifications.utils import create_notification

from .models import Course, Enrollment, CourseReview, CourseDiscussion, Payment
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseReviewSerializer,
    CourseDiscussionSerializer,
    PaymentSerializer,
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

class ContinueLearningView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "student_profile"):
            return Response([])

        enrollments = Enrollment.objects.filter(
            student=request.user.student_profile,
            course__is_published=True
        ).select_related("course").order_by("-enrolled_at")

        courses = []

        for enrollment in enrollments:
            serializer = CourseListSerializer(
                enrollment.course,
                context={"request": request}
            )

            item = serializer.data
            item["progress_percentage"] = enrollment.progress_percentage or 0
            item["completed"] = enrollment.completed
            courses.append(item)

        return Response(courses)

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

        student = request.user.student_profile
        teacher_user = course.teacher.user

        create_notification(
            request.user,
            "Welcome to the course",
            f"You are now enrolled in {course.title}. You can start learning now."
        )

        create_notification(
            teacher_user,
            "New student enrolled",
            f"{student} enrolled in your course {course.title}."
        )

        return Response(
            {
                "detail":
                "Enrollment successful."
            },
            status=status.HTTP_201_CREATED
        )
    
class BuyCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        if not hasattr(request.user, "student_profile"):
            return Response(
                {"detail": "Only students can buy courses."},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student_profile

        try:
            course = Course.objects.get(
                id=course_id,
                is_published=True
            )
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if course.is_free:
            return Response(
                {"detail": "This course is free. Use enroll instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Enrollment.objects.filter(student=student, course=course).exists():
            return Response(
                {"detail": "Already enrolled."},
                status=status.HTTP_200_OK
            )

        payment, created = Payment.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                "amount": course.price,
                "status": "paid",
            }
        )

        payment.amount = course.price
        payment.status = "paid"
        payment.save()

        Enrollment.objects.create(
            student=student,
            course=course
        )

        create_notification(
            request.user,
            "Payment successful",
            f"You bought {course.title}. You can start learning now."
        )

        create_notification(
            course.teacher.user,
            "New course purchase",
            f"{student} bought your course {course.title}."
        )

        serializer = PaymentSerializer(payment)

        return Response(
            {
                "detail": "Payment successful. You are enrolled.",
                "payment": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )
    
class CourseReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        reviews = CourseReview.objects.filter(
            course_id=course_id
        ).select_related("student")

        my_review = None

        if hasattr(request.user, "student_profile"):
            my_review = CourseReview.objects.filter(
                course_id=course_id,
                student=request.user.student_profile
            ).first()

        return Response({
            "reviews": CourseReviewSerializer(
                reviews,
                many=True
            ).data,
            "my_review": CourseReviewSerializer(my_review).data
            if my_review else None,
        })

    def post(self, request, course_id):
        if not hasattr(request.user, "student_profile"):
            return Response(
                {"detail": "Only students can review courses."},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student_profile

        enrollment = Enrollment.objects.filter(
            student=student,
            course_id=course_id,
            completed=True
        ).first()

        if not enrollment:
            enrollment = Enrollment.objects.filter(
                student=student,
                course_id=course_id,
                progress_percentage=100
            ).first()

        if enrollment and not enrollment.completed:
            enrollment.completed = True
            enrollment.save(update_fields=["completed"])

        if not enrollment:
            return Response(
                {
                    "detail":
                    "You can review this course only after completing and passing it."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        review, created = CourseReview.objects.update_or_create(
            student=student,
            course_id=course_id,
            defaults={
                "rating": request.data.get("rating"),
                "review": request.data.get("review", ""),
            }
        )

        serializer = CourseReviewSerializer(review)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
class CourseDiscussionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _can_access_discussion(self, user, course):
        if hasattr(user, "teacher_profile"):
            return course.teacher == user.teacher_profile

        if hasattr(user, "student_profile"):
            return Enrollment.objects.filter(
                student=user.student_profile,
                course=course
            ).exists()

        return False

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_access_discussion(request.user, course):
            return Response(
                {"detail": "You cannot access this discussion."},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = CourseDiscussion.objects.filter(course=course)

        serializer = CourseDiscussionSerializer(
            messages,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_access_discussion(request.user, course):
            return Response(
                {"detail": "You cannot write in this discussion."},
                status=status.HTTP_403_FORBIDDEN
            )

        message = request.data.get("message", "").strip()

        if not message:
            return Response(
                {"detail": "Message is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        discussion = CourseDiscussion.objects.create(
            course=course,
            user=request.user,
            message=message
        )

        serializer = CourseDiscussionSerializer(
            discussion,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)