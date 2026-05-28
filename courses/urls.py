from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ContinueLearningView,
    CourseDiscussionView,
    CourseReviewView,
    CourseViewSet,
    PublishedCoursesView,
    EnrollCourseView
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = router.urls + [
    path(
        "student/courses/",
        PublishedCoursesView.as_view(),
        name="student-courses",
    ),

    path(
        "student/courses/<int:course_id>/enroll/",
        EnrollCourseView.as_view(),
        name="enroll-course",
    ),
    path("continue-learning/", ContinueLearningView.as_view(), name="continue-learning"),
    path(
    "courses/<int:course_id>/reviews/",
    CourseReviewView.as_view(),
    name="course-reviews",
   ),
    path(
    "courses/<int:course_id>/discussions/",
    CourseDiscussionView.as_view(),
    name="course-discussions",
   ),
]