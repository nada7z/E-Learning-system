from rest_framework import serializers
from courses.models import Enrollment
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()
    graded_count = serializers.SerializerMethodField()
    avg_grade = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "description",
            "deadline",
            "max_score",
            "submissions_count",
            "enrolled_count",
            "graded_count",
            "avg_grade",
            "created_at",
        ]

    def get_course_title(self, obj):
        return obj.course.title

    def get_submissions_count(self, obj):
        return Submission.objects.filter(assignment=obj).count()

    def get_enrolled_count(self, obj):
        return Enrollment.objects.filter(course=obj.course).count()

    def get_graded_count(self, obj):
        return Submission.objects.filter(
            assignment=obj,
            grade__isnull=False
        ).count()

    def get_avg_grade(self, obj):
        submissions = Submission.objects.filter(
            assignment=obj,
            grade__isnull=False
        )

        if not submissions.exists():
            return None

        total = sum(s.grade for s in submissions)
        return round(total / submissions.count(), 1)


class SubmissionSerializer(serializers.ModelSerializer):
    assignment_id = serializers.IntegerField(source="assignment.id", read_only=True)
    student_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    avatar_color = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "assignment_id",
            "student",
            "student_name",
            "text_answer",
            "file",
            "file_url",
            "file_name",
            "submitted_at",
            "grade",
            "feedback",
            "avatar_color",
        ]

        read_only_fields = [
            "student",
            "submitted_at",
        ]

    def get_student_name(self, obj):
        return str(obj.student)

    def get_file_url(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return ""

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url

    def get_file_name(self, obj):
        if not obj.file:
            return "No file"

        return obj.file.name.split("/")[-1]

    def get_avatar_color(self, obj):
        return "#3D5AFE"

    def validate(self, data):
        text_answer = data.get("text_answer", "")
        file = data.get("file", None)

        if not text_answer and not file:
            raise serializers.ValidationError(
                "You must either write an answer or upload a file."
            )

        return data