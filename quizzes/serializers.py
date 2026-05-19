from rest_framework import serializers

from .models import (
    Quiz,
    Question,
    AnswerOption,
    QuizAttempt,
    StudentAnswer,
)


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = [
            "id",
            "text",
            "is_correct",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "points",
            "order_number",
            "options",
        ]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])

        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            AnswerOption.objects.create(
                question=question,
                **option_data
            )

        return question


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(
        many=True,
        required=False
    )

    course_title = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    attempts_count = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "course_title",
            "lesson",
            "title",
            "description",
            "passing_score",
            "time_limit_minutes",
            "is_published",
            "questions",
            "questions_count",
            "attempts_count",
            "pass_rate",
            "created_at",
        ]

    def get_course_title(self, obj):
        return obj.course.title

    def get_questions_count(self, obj):
        return obj.questions.count()

    def get_attempts_count(self, obj):
        return obj.attempts.count()

    def get_pass_rate(self, obj):
        total = obj.attempts.count()

        if total == 0:
            return 0

        passed = obj.attempts.filter(passed=True).count()

        return round((passed / total) * 100)

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])

        quiz = Quiz.objects.create(**validated_data)

        self._save_questions(quiz, questions_data)

        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if questions_data is not None:
            instance.questions.all().delete()
            self._save_questions(instance, questions_data)

        return instance

    def _save_questions(self, quiz, questions_data):
        for index, question_data in enumerate(questions_data, start=1):
            question_data.pop("id", None)
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
                    index
                ),
            )

            for option_data in options_data:
                option_data.pop("id", None)

                AnswerOption.objects.create(
                    question=question,
                    text=option_data.get("text", ""),
                    is_correct=option_data.get("is_correct", False),
                )


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = [
            "question",
            "selected_option",
            "text_answer",
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(
        many=True,
        required=False
    )

    quiz_id = serializers.IntegerField(
        source="quiz.id",
        read_only=True
    )

    quiz_title = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    avatar_color = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "quiz_id",
            "quiz_title",
            "student_name",
            "answers",
            "score",
            "passed",
            "submitted_at",
            "avatar_color",
        ]

        read_only_fields = [
            "score",
            "passed",
            "submitted_at",
        ]

    def get_quiz_title(self, obj):
        return obj.quiz.title

    def get_student_name(self, obj):
        return str(obj.student)

    def get_avatar_color(self, obj):
        return "#3D5AFE"

    def create(self, validated_data):
        answers_data = validated_data.pop("answers", [])

        request = self.context.get("request")

        student = request.user.student_profile

        quiz = validated_data["quiz"]

        attempt = QuizAttempt.objects.create(
            student=student,
            **validated_data
        )

        total_points = 0
        earned_points = 0

        for answer_data in answers_data:
            question = answer_data["question"]
            selected_option = answer_data.get("selected_option")
            text_answer = answer_data.get("text_answer", "")

            is_correct = False
            points = 0

            total_points += question.points

            if selected_option:
                if selected_option.is_correct:
                    is_correct = True
                    points = question.points

            elif text_answer:
                correct_answer = question.options.filter(
                    is_correct=True
                ).first()

                if correct_answer:
                    if (
                        text_answer.strip().lower()
                        ==
                        correct_answer.text.strip().lower()
                    ):
                        is_correct = True
                        points = question.points

            earned_points += points

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                text_answer=text_answer,
                is_correct=is_correct,
                earned_points=points,
            )

        percentage = 0

        if total_points > 0:
            percentage = (earned_points / total_points) * 100

        attempt.score = percentage
        attempt.passed = percentage >= quiz.passing_score
        attempt.save()

        return attempt