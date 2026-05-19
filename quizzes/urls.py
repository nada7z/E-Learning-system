from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import QuizViewSet, QuizAttemptViewSet

router = DefaultRouter()

router.register(
    "quizzes",
    QuizViewSet,
    basename="quizzes"
)

router.register(
    "quiz-attempts",
    QuizAttemptViewSet,
    basename="quiz-attempts"
)

urlpatterns = [
    path("", include(router.urls)),
]