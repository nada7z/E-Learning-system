from urllib import request
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from courses.models import Course
from notifications.utils import create_notification
from .models import Certificate
from .serializers import CertificateSerializer


class MyCertificatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "student_profile"):
            return Response([])

        certificates = Certificate.objects.filter(
            student=request.user.student_profile
        ).order_by("-issued_at")

        serializer = CertificateSerializer(
            certificates,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class GenerateCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, "student_profile"):
            return Response(
                {"detail": "Only students can earn certificates."},
                status=status.HTTP_403_FORBIDDEN
            )

        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"detail": "course_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        certificate, created = Certificate.objects.get_or_create(
            student=request.user.student_profile,
            course=course,
            defaults={
                "certificate_code": f"CERT-{uuid.uuid4().hex[:12].upper()}"
            }
        )

        if created:
            create_notification(
                request.user,
                "Certificate ready",
                f"Congratulations! Your certificate for {course.title} is ready."
            ) 

        serializer = CertificateSerializer(
            certificate,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)