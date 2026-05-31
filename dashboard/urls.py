from django.urls import path
from .views import AdminReportsView, AdminUsersView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("users/", AdminUsersView.as_view(), name="admin-users"),
    path("reports/", AdminReportsView.as_view(), name="admin-reports"),
]