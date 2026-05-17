from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
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
]