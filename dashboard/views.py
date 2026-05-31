from collections import defaultdict
from datetime import timedelta

from django.db.models import Avg, Count
from django.db.models import Sum
from courses.models import Payment
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from courses.models import Course, Enrollment
from accounts.models import User
from assignments.models import Assignment, Submission
from courses.models import (
    Course,
    Enrollment,
    CourseReview,
)
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
            "level": course.level,
            "duration_hours": course.duration_hours,
            "price": course.price,
            "is_published": course.is_published,
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
       
        avg_rating = (
            CourseReview.objects
            .filter(course__teacher=teacher)
            .aggregate(avg=Avg("rating"))
            .get("avg")
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
                "avg_rating": round(avg_rating, 1) if avg_rating else 0,
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
    
class AdminUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "Only admins can view users."},
                status=403
            )

        users = []
        now = timezone.now()

        for u in User.objects.all().order_by("-date_joined"):
            courses_count = 0

            if hasattr(u, "student_profile"):
                courses_count = Enrollment.objects.filter(
                    student=u.student_profile
                ).count()

            if hasattr(u, "teacher_profile"):
                courses_count = Course.objects.filter(
                    teacher=u.teacher_profile
                ).count()

            if getattr(u, "account_status", "normal") == "banned":
                user_status = "banned"

            elif (
                getattr(u, "account_status", "normal") == "suspended"
                and getattr(u, "suspended_until", None)
                and u.suspended_until > now
            ):
                user_status = "suspended"

            elif u.last_login and u.last_login >= now - timedelta(days=30):
                user_status = "active"

            else:
                user_status = "inactive"

            users.append({
                "id": u.id,
                "name": u.get_full_name() or u.email,
                "email": u.email,
                "role": u.role,
                "courses_count": courses_count,
                "joined": u.date_joined,
                "last_login": u.last_login,
                "status": user_status,
                "suspended_until": getattr(u, "suspended_until", None),
            })

        return Response(users)
    
class AdminUserActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if getattr(request.user, "role", None) != "admin":
            return Response({"detail": "Only admins can manage users."}, status=403)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        action = request.data.get("action")
        days = int(request.data.get("days") or 0)

        if action == "suspend":
            if days <= 0:
                return Response({"detail": "Suspension duration is required."}, status=400)

            user.account_status = "suspended"
            user.suspended_until = timezone.now() + timedelta(days=days)
            user.save(update_fields=["account_status", "suspended_until"])

            return Response({"detail": f"User suspended for {days} days."})

        if action == "ban":
            user.account_status = "banned"
            user.suspended_until = None
            user.save(update_fields=["account_status", "suspended_until"])

            return Response({"detail": "User banned."})

        if action == "restore":
            user.account_status = "normal"
            user.suspended_until = None
            user.save(update_fields=["account_status", "suspended_until"])

            return Response({"detail": "User restored."})

        return Response({"detail": "Invalid action."}, status=400)
    
class AdminReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", None) != "admin":
            return Response({"detail": "Only admins can view reports."}, status=403)

        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()

        total_revenue = (
            Payment.objects
            .filter(status="paid")
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )

        user_growth = (
            User.objects
            .annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(value=Count("id"))
            .order_by("month")
        )

        enrollment_growth = (
            Enrollment.objects
            .annotate(month=TruncMonth("enrolled_at"))
            .values("month")
            .annotate(value=Count("id"))
            .order_by("month")
        )

        top_courses = []

        for course in Course.objects.all():
            students_count = Enrollment.objects.filter(course=course).count()

            avg_rating = (
                CourseReview.objects
                .filter(course=course)
                .aggregate(avg=Avg("rating"))
                .get("avg")
                or 0
            )

            top_courses.append({
                "id": course.id,
                "title": course.title,
                "teacher": str(course.teacher),
                "students": students_count,
                "rating": round(avg_rating, 1),
                "published": course.is_published,
            })

        top_courses = sorted(
            top_courses,
            key=lambda item: item["students"],
            reverse=True
        )[:8]

        return Response({
            "stats": {
                "total_users": total_users,
                "total_courses": total_courses,
                "total_enrollments": total_enrollments,
                "total_revenue": float(total_revenue),
            },
            "user_growth": [
                {
                    "label": row["month"].strftime("%b") if row["month"] else "",
                    "value": row["value"],
                }
                for row in user_growth
            ],
            "enrollment_growth": [
                {
                    "label": row["month"].strftime("%b") if row["month"] else "",
                    "value": row["value"],
                }
                for row in enrollment_growth
            ],
            "top_courses": top_courses,
        })


