from django.urls import path
from .views import AdminReportsView, AdminUserActionView, AdminUsersView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("users/", AdminUsersView.as_view(), name="admin-users"),
    path("users/<int:user_id>/action/", AdminUserActionView.as_view(), name="dashboard-user-action"),
    path("reports/", AdminReportsView.as_view(), name="admin-reports"),
]