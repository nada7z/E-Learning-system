# dashboard/serializers.py
from rest_framework import serializers
from .models import ActivityLog
from accounts.models import User
from courses.models import Course, Enrollment  # adjust import based on your apps


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'timestamp']


class DashboardStatsSerializer(serializers.Serializer):
    # Common stats
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    recent_activities = ActivityLogSerializer(many=True)


# Student Dashboard
class StudentDashboardSerializer(serializers.Serializer):
    enrolled_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()
    avg_quiz_score = serializers.FloatField()
    progress = serializers.FloatField()
    recent_activities = ActivityLogSerializer(many=True)


# Teacher Dashboard
class TeacherDashboardSerializer(serializers.Serializer):
    active_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    pending_grading = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    recent_activities = ActivityLogSerializer(many=True)


# Admin Dashboard
class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_completions = serializers.IntegerField()
    total_revenue = serializers.IntegerField()  # if you have payments later
    recent_activities = ActivityLogSerializer(many=True)