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

    options = AnswerOptionSerializer(
        many=True
    )

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
        options_data = validated_data.pop("options")

        question = Question.objects.create(
            **validated_data
        )

        for option_data in options_data:
            AnswerOption.objects.create(
                question=question,
                **option_data
            )

        return question


class QuizSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(
        many=True
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "course",
            "lesson",
            "title",
            "description",
            "passing_score",
            "time_limit_minutes",
            "is_published",
            "questions",
            "created_at",
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")

        quiz = Quiz.objects.create(
            **validated_data
        )

        for question_data in questions_data:

            options_data = question_data.pop(
                "options"
            )

            question = Question.objects.create(
                quiz=quiz,
                **question_data
            )

            for option_data in options_data:
                AnswerOption.objects.create(
                    question=question,
                    **option_data
                )

        return quiz


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
        many=True
    )

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "answers",
            "score",
            "passed",
            "submitted_at",
        ]

        read_only_fields = [
            "score",
            "passed",
            "submitted_at",
        ]

    def create(self, validated_data):

        answers_data = validated_data.pop(
            "answers"
        )

        request = self.context.get("request")

        student = request.user.student

        quiz = validated_data["quiz"]

        attempt = QuizAttempt.objects.create(
            student=student,
            **validated_data
        )

        total_points = 0
        earned_points = 0

        for answer_data in answers_data:

            question = answer_data["question"]

            selected_option = answer_data.get(
                "selected_option"
            )

            text_answer = answer_data.get(
                "text_answer",
                ""
            )

            is_correct = False
            points = 0

            total_points += question.points

            # MULTIPLE CHOICE / TRUE FALSE
            if selected_option:

                if selected_option.is_correct:
                    is_correct = True
                    points = question.points

            # SHORT ANSWER
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
            percentage = (
                earned_points / total_points
            ) * 100

        attempt.score = percentage

        attempt.passed = (
            percentage >= quiz.passing_score
        )

        attempt.save()

        return attempt