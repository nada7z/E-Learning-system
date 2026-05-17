from rest_framework import serializers

from .models import Course
from lessons.models import Lesson

from quizzes.models import Quiz, Question, AnswerOption
from assignments.models import Assignment


class AnswerOptionNestedSerializer(serializers.Serializer):
    text = serializers.CharField()
    is_correct = serializers.BooleanField(default=False)


class QuestionNestedSerializer(serializers.Serializer):
    text = serializers.CharField()
    question_type = serializers.CharField(default="multiple_choice")
    points = serializers.IntegerField(default=1)
    order_number = serializers.IntegerField(required=False)
    options = AnswerOptionNestedSerializer(many=True, required=False)


class QuizNestedSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    passing_score = serializers.IntegerField(default=50)
    time_limit_minutes = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    questions = QuestionNestedSerializer(many=True, required=False)


class AssignmentNestedSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    instructions = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    max_score = serializers.IntegerField(default=100)


class LessonCreateSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_blank=True)
    meta = serializers.CharField(required=False, allow_blank=True)

    quiz = QuizNestedSerializer(required=False, allow_null=True)
    assignment = AssignmentNestedSerializer(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content",
            "video_url",
            "video_file",
            "lesson_type",
            "order_number",
            "is_preview",
            "type",
            "meta",
            "quiz",
            "assignment",
        ]

        extra_kwargs = {
            "content": {
                "required": False,
                "allow_blank": True,
            },
            "video_url": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "video_file": {
                "required": False,
                "allow_null": True,
            },
            "lesson_type": {
                "required": False,
            },
            "order_number": {
                "required": False,
            },
            "is_preview": {
                "required": False,
            },
        }


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonCreateSerializer(
        many=True,
        required=False
    )

    teacher_name = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "title",
            "description",
            "category",
            "thumbnail",
            "level",
            "language",
            "duration_hours",
            "has_certificate",
            "tags",
            "lessons",
            "lessons_count",
            "is_free",
            "price",
            "is_published",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "teacher",
            "created_at",
            "updated_at",
        ]

    def get_teacher_name(self, obj):
        return str(obj.teacher)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def create(self, validated_data):
        lessons_data = validated_data.pop("lessons", [])

        course = Course.objects.create(**validated_data)

        for index, lesson_data in enumerate(lessons_data, start=1):
            lesson_data.pop("id", None)
            lesson_data.pop("meta", None)

            frontend_type = lesson_data.pop("type", None)
            quiz_data = lesson_data.pop("quiz", None)
            assignment_data = lesson_data.pop("assignment", None)

            lesson_type = lesson_data.get("lesson_type") or frontend_type or "reading"

            lesson = Lesson.objects.create(
                course=course,
                title=lesson_data.get("title", f"Lesson {index}"),
                content=lesson_data.get("content", ""),
                video_url=lesson_data.get("video_url"),
                video_file=lesson_data.get("video_file"),
                lesson_type=lesson_type,
                order_number=lesson_data.get("order_number", index),
                is_preview=lesson_data.get("is_preview", False),
            )

            if lesson_type == "quiz" and quiz_data:
                quiz = Quiz.objects.create(
                    course=course,
                    lesson=lesson,
                    title=quiz_data.get("title") or lesson.title,
                    description=quiz_data.get("description", ""),
                    passing_score=quiz_data.get("passing_score", 50),
                    time_limit_minutes=quiz_data.get("time_limit_minutes"),
                    is_published=True,
                )

                for q_index, question_data in enumerate(
                    quiz_data.get("questions", []),
                    start=1
                ):
                    options_data = question_data.pop("options", [])

                    question = Question.objects.create(
                        quiz=quiz,
                        text=question_data.get("text", ""),
                        question_type=question_data.get(
                            "question_type",
                            "multiple_choice"
                        ),
                        points=question_data.get("points", 1),
                        order_number=question_data.get(
                            "order_number",
                            q_index
                        ),
                    )

                    for option_data in options_data:
                        AnswerOption.objects.create(
                            question=question,
                            text=option_data.get("text", ""),
                            is_correct=option_data.get("is_correct", False),
                        )

            if lesson_type == "assignment" and assignment_data:
                Assignment.objects.create(
                    course=course,
                    lesson=lesson,
                    title=assignment_data.get("title") or lesson.title,
                    instructions=assignment_data.get("instructions", ""),
                    due_date=assignment_data.get("due_date"),
                    max_score=assignment_data.get("max_score", 100),
                )

        return course