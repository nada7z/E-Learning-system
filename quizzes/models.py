from django.db import models

from courses.models import Course
from lessons.models import Lesson
from accounts.models import Student


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )

    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quiz",
        blank=True,
        null=True
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    passing_score = models.PositiveIntegerField(default=50)

    time_limit_minutes = models.PositiveIntegerField(
        blank=True,
        null=True
    )
     
    is_final_exam = models.BooleanField(default=False)
    
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ("multiple_choice", "Multiple Choice"),
        ("true_false", "True / False"),
        ("short_answer", "Short Answer"),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    text = models.TextField()

    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPES,
        default="multiple_choice"
    )

    points = models.PositiveIntegerField(default=1)

    order_number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order_number"]

    def __str__(self):
        return self.text[:50]


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )

    text = models.CharField(max_length=255)

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )

    score = models.FloatField(default=0)

    passed = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} - {self.quiz}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    text_answer = models.TextField(blank=True)

    is_correct = models.BooleanField(default=False)

    earned_points = models.FloatField(default=0)

    def __str__(self):
        return f"{self.attempt} - {self.question}"