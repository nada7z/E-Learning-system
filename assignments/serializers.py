from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "lesson",
            "title",
            "instructions",
            "due_date",
            "max_score",
            "created_at",
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "student",
            "text_answer",
            "file",
            "submitted_at",
            "grade",
            "feedback",
        ]

        read_only_fields = [
            "student",
            "submitted_at",
            "grade",
            "feedback",
        ]

    def validate(self, data):
        text_answer = data.get("text_answer", "")
        file = data.get("file", None)

        if not text_answer and not file:
            raise serializers.ValidationError(
                "You must either write an answer or upload a file."
            )

        return data