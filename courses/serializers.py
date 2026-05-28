from rest_framework import serializers

from .models import Course, CourseReview, Enrollment, CourseDiscussion
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

    options = AnswerOptionNestedSerializer(
        many=True,
        required=False
    )


class QuizNestedSerializer(serializers.Serializer):
    title = serializers.CharField(
        required=False,
        allow_blank=True
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    passing_score = serializers.IntegerField(default=50)

    time_limit_minutes = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    is_final_exam = serializers.BooleanField(default=False)

    questions = QuestionNestedSerializer(
        many=True,
        required=False
    )


class AssignmentNestedSerializer(serializers.Serializer):
    title = serializers.CharField(
        required=False,
        allow_blank=True
    )

    instructions = serializers.CharField(
        required=False,
        allow_blank=True
    )

    due_date = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    max_score = serializers.IntegerField(default=100)


class LessonCreateSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_blank=True)
    meta = serializers.CharField(required=False, allow_blank=True)

    quiz = serializers.SerializerMethodField()

    assignment = AssignmentNestedSerializer(
        required=False,
        allow_null=True
    )

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
            "content": {"required": False, "allow_blank": True},
            "video_url": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "video_file": {
                "required": False,
                "allow_null": True,
            },
            "lesson_type": {"required": False},
            "order_number": {"required": False},
            "is_preview": {"required": False},
        }

    def get_quiz(self, obj):
        quiz = getattr(obj, "quiz", None)

        if not quiz:
            return None

        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "passing_score": quiz.passing_score,
            "time_limit_minutes": quiz.time_limit_minutes,
            "is_final_exam": quiz.is_final_exam,
            "questions": [
                {
                    "id": question.id,
                    "text": question.text,
                    "question_type": question.question_type,
                    "points": question.points,
                    "order_number": question.order_number,
                    "options": [
                        {
                            "id": option.id,
                            "text": option.text,
                            "is_correct": option.is_correct,
                        }
                        for option in question.options.all()
                    ],
                }
                for question in quiz.questions.all()
            ],
        }


class CourseSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False, allow_null=True)

    lessons = LessonCreateSerializer(
        many=True,
        required=False
    )

    teacher_name = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

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
            "is_enrolled",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "teacher",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if instance.thumbnail:
            data["thumbnail"] = (
                request.build_absolute_uri(instance.thumbnail.url)
                if request
                else instance.thumbnail.url
            )
        else:
            data["thumbnail"] = None

        return data

    def get_teacher_name(self, obj):
        return str(obj.teacher)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_enrolled(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        if not hasattr(request.user, "student_profile"):
            return False

        return Enrollment.objects.filter(
            student=request.user.student_profile,
            course=obj
        ).exists()

    def create(self, validated_data):
        lessons_data = validated_data.pop("lessons", [])

        course = Course.objects.create(**validated_data)

        self._save_lessons(course, lessons_data)

        return course

    def update(self, instance, validated_data):
        request = self.context.get("request")
        lessons_data = validated_data.pop("lessons", None)

        if request:
            remove_thumbnail = request.data.get("remove_thumbnail")

            if remove_thumbnail == "true":
                if instance.thumbnail:
                    instance.thumbnail.delete(save=False)

                instance.thumbnail = None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if lessons_data is not None:
            instance.lessons.all().delete()
            self._save_lessons(instance, lessons_data)

        return instance

    def _save_lessons(self, course, lessons_data):
        for index, lesson_data in enumerate(lessons_data, start=1):
            lesson_data.pop("id", None)
            lesson_data.pop("meta", None)

            frontend_type = lesson_data.pop("type", None)

            quiz_data = lesson_data.pop("quiz", None)
            assignment_data = lesson_data.pop("assignment", None)

            lesson_type = (
                lesson_data.get("lesson_type")
                or frontend_type
                or "reading"
            )

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
                    is_final_exam=quiz_data.get("is_final_exam", False),
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

class CourseListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    teacher_name = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course

        fields = [
            "id",
            "title",
            "description",
            "category",
            "thumbnail",
            "level",
            "language",
            "duration_hours",
            "has_certificate",
            "teacher_name",
            "lessons_count",
            "enrolled_count",
            "is_free",
            "price",
            "is_enrolled",
        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)

            return obj.thumbnail.url

        return None

    def get_teacher_name(self, obj):
        return str(obj.teacher)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_enrolled_count(self, obj):
        return Enrollment.objects.filter(course=obj).count()

    def get_is_enrolled(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        if not hasattr(request.user, "student_profile"):
            return False

        return Enrollment.objects.filter(
            student=request.user.student_profile,
            course=obj
        ).exists()
        
class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseReview
        fields = [
            "id",
            "course",
            "student",
            "student_name",
            "rating",
            "review",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["course", "student", "created_at", "updated_at"]

    def get_student_name(self, obj):
        return str(obj.student)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
class CourseDiscussionSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()

    class Meta:
        model = CourseDiscussion
        fields = [
            "id",
            "course",
            "user",
            "message",
            "author_name",
            "author_role",
            "is_teacher",
            "created_at",
        ]
        read_only_fields = [
            "course",
            "user",
            "author_name",
            "author_role",
            "is_teacher",
            "created_at",
        ]

    def get_author_name(self, obj):
        if hasattr(obj.user, "teacher_profile"):
            return str(obj.user.teacher_profile)

        if hasattr(obj.user, "student_profile"):
            return str(obj.user.student_profile)

        return obj.user.email

    def get_is_teacher(self, obj):
        return (
            hasattr(obj.user, "teacher_profile")
            and obj.course.teacher == obj.user.teacher_profile
        )

    def get_author_role(self, obj):
        if self.get_is_teacher(obj):
            return "Teacher"

        return "Student"