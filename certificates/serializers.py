from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            "id",
            "course",
            "course_title",
            "student",
            "student_name",
            "certificate_code",
            "pdf_url",
            "issued_at",
        ]

    def get_course_title(self, obj):
        return obj.course.title

    def get_student_name(self, obj):
        user = obj.student.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or user.email

    def get_pdf_url(self, obj):
        request = self.context.get("request")

        if not obj.pdf_file:
            return ""

        if request:
            return request.build_absolute_uri(obj.pdf_file.url)

        return obj.pdf_file.url