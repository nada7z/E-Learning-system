# accounts/urls.py
from django.urls import path
from .views import LoginView, RegisterView

urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),      # Login (JWT)
    path('register/', RegisterView.as_view(), name='register'),
]