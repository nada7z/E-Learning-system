from django.urls import path
from .views import MyCertificatesView, GenerateCertificateView

urlpatterns = [
    path("my-certificates/", MyCertificatesView.as_view(), name="my-certificates"),
    path("generate/", GenerateCertificateView.as_view(), name="generate-certificate"),
]