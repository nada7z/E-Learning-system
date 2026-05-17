from collections import defaultdict
from datetime import timedelta

from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from assignments.models import Assignment, Submission
from courses.models import Course, Enrollment
from lessons.models import Lesson
from quizzes.models import QuizAttempt
from .models import ActivityLog


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", None)

        ActivityLog.objects.create(
            user=user,
            action=f"Accessed {str(role).capitalize()} Dashboard",
        )

        if role == "student":
            data = self.get_student_dashboard(user)
        elif role == "teacher":
            data = self.get_teacher_dashboard(user)
        elif role == "admin":
            data = self.get_admin_dashboard()
        else:
            return Response({"error": "Invalid role"}, status=400)

        return Response(data)

    def _activity_rows(self, queryset, include_user=False):
        rows = []
        values = ["action", "timestamp"]

        if include_user:
            values.append("user__email")

        for item in queryset.values(*values):
            row = {
                "action": item["action"],
                "timestamp": item["timestamp"],
            }

            if include_user:
                row["user_email"] = item.get("user__email")

            rows.append(row)

        return rows

    def _course_payload(self, course, progress=None, student_count=None):
        teacher_user = getattr(getattr(course, "teacher", None), "user", None)

        teacher_name = (
            getattr(teacher_user, "get_full_name", lambda: "")()
            or getattr(teacher_user, "email", "")
            or str(getattr(course, "teacher", ""))
        )

        lessons_count = Lesson.objects.filter(course=course).count()

        payload = {
            "id": course.id,
            "title": course.title,
            "category": course.category,
            "teacher": teacher_name,
            "lessons": lessons_count,
            "thumbnail": course.thumbnail.url if getattr(course, "thumbnail", None) else None,
        }

        if progress is not None:
            payload["progress"] = round(progress or 0, 1)

        if student_count is not None:
            payload["students"] = student_count

        return payload

    def get_student_dashboard(self, user):
        student = user.student_profile

        enrollments = (
            Enrollment.objects
            .filter(student=student)
            .select_related("course", "course__teacher")
            .order_by("-enrolled_at")
        )

        enrolled_courses = enrollments.count()
        completed_courses = enrollments.filter(completed=True).count()

        pending_assignments = (
            Assignment.objects
            .filter(course__enrollment__student=student, deadline__gte=timezone.now())
            .exclude(submission__student=student)
            .distinct()
            .count()
        )

        avg_quiz_score = (
            QuizAttempt.objects
            .filter(student=student)
            .aggregate(avg_score=Avg("score"))
            .get("avg_score")
            or 0
        )

        progress = enrollments.aggregate(
            avg_progress=Avg("progress_percentage")
        ).get("avg_progress") or 0

        in_progress_courses = [
            self._course_payload(
                enrollment.course,
                progress=enrollment.progress_percentage,
            )
            for enrollment in enrollments
            if 0 < (enrollment.progress_percentage or 0) < 100
        ][:5]

        progress_chart = list(
            enrollments
            .annotate(month=TruncMonth("enrolled_at"))
            .values("month")
            .annotate(value=Avg("progress_percentage"))
            .order_by("month")
        )

        quiz_scores = list(
            QuizAttempt.objects
            .filter(student=student)
            .select_related("quiz")
            .order_by("-submitted_at")[:8]
            .values("quiz__title", "score", "submitted_at")
        )

        quiz_scores.reverse()

        return {
            "role": "student",
            "stats": {
                "enrolled_courses": enrolled_courses,
                "completed_courses": completed_courses,
                "pending_assignments": pending_assignments,
                "avg_quiz_score": round(avg_quiz_score, 1),
                "progress": round(progress, 1),
            },
            "in_progress_courses": in_progress_courses,
            "progress_chart": [
                {
                    "label": row["month"].strftime("%b") if row["month"] else "",
                    "value": round(row["value"] or 0, 1),
                }
                for row in progress_chart
            ],
            "quiz_scores": [
                {
                    "label": row["quiz__title"] or "Quiz",
                    "value": round(row["score"] or 0, 1),
                    "submitted_at": row["submitted_at"],
                }
                for row in quiz_scores
            ],
            "recent_activities": self._activity_rows(
                ActivityLog.objects.filter(user=user).order_by("-timestamp")[:5]
            ),
        }

    def get_teacher_dashboard(self, user):
        teacher = user.teacher_profile

        courses = Course.objects.filter(teacher=teacher).order_by("-created_at")
        active_courses = courses.count()

        total_students = (
            Enrollment.objects
            .filter(course__teacher=teacher)
            .values("student")
            .distinct()
            .count()
        )

        pending_grading = (
            Submission.objects
            .filter(assignment__course__teacher=teacher, grade__isnull=True)
            .count()
        )

        course_rows = []

        for course in courses:
            course_rows.append(
                self._course_payload(
                    course,
                    student_count=Enrollment.objects.filter(course=course).count(),
                )
            )

        enrollment_trends = list(
            Enrollment.objects
            .filter(
                course__teacher=teacher,
                enrolled_at__gte=timezone.now() - timedelta(weeks=8),
            )
            .annotate(week=TruncWeek("enrolled_at"))
            .values("week", "course__title")
            .annotate(value=Count("id"))
            .order_by("week", "course__title")
        )

        labels = []
        week_totals = defaultdict(lambda: defaultdict(int))

        for row in enrollment_trends:
            label = row["week"].strftime("%b %d") if row["week"] else ""
            labels.append(label)
            week_totals[row["course__title"] or "Course"][label] += row["value"]

        labels = list(dict.fromkeys(labels))

        datasets = {
            course_title: [totals.get(label, 0) for label in labels]
            for course_title, totals in week_totals.items()
        }

        return {
            "role": "teacher",
            "stats": {
                "active_courses": active_courses,
                "total_students": total_students,
                "pending_grading": pending_grading,
                "avg_rating": None,
            },
            "courses": course_rows,
            "enrollment_trends": {
                "labels": labels,
                "datasets": [
                    {"label": label, "data": data}
                    for label, data in datasets.items()
                ],
            },
            "recent_activities": self._activity_rows(
                ActivityLog.objects.filter(user=user).order_by("-timestamp")[:5]
            ),
        }

    def get_admin_dashboard(self):
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_completions = Enrollment.objects.filter(completed=True).count()

        active_users_today = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=1)
        ).count()

        course_distribution = list(
            Course.objects
            .values("category")
            .annotate(value=Count("id"))
            .order_by("-value")
        )

        user_growth = list(
            User.objects
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(value=Count("id"))
            .order_by("month")
        )

        recent_users = []

        for u in User.objects.order_by("-date_joined")[:5]:
            recent_users.append(
                {
                    "id": u.id,
                    "name": getattr(u, "get_full_name", lambda: "")()
                    or getattr(u, "email", ""),
                    "email": getattr(u, "email", ""),
                    "role": getattr(u, "role", ""),
                    "joined": getattr(u, "date_joined", None),
                    "last_login": getattr(u, "last_login", None),
                }
            )

        return {
            "role": "admin",
            "stats": {
                "total_users": total_users,
                "total_courses": total_courses,
                "total_enrollments": total_enrollments,
                "total_completions": total_completions,
                "active_users_today": active_users_today,
                "total_revenue": 0,
            },
            "user_growth": [
                {
                    "label": row["month"].strftime("%b") if row["month"] else "",
                    "value": row["value"],
                }
                for row in user_growth
            ],
            "course_distribution": [
                {
                    "label": row["category"] or "Uncategorized",
                    "value": row["value"],
                }
                for row in course_distribution
            ],
            "recent_users": recent_users,
            "recent_activities": self._activity_rows(
                ActivityLog.objects.all().order_by("-timestamp")[:10],
                include_user=True,
            ),
        }