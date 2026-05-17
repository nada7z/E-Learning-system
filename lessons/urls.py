from rest_framework.routers import DefaultRouter
from .views import LessonViewSet

router = DefaultRouter()
router.register("", LessonViewSet)

urlpatterns = router.urls