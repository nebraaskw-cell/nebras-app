from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CircleViewSet, CycleViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register("circles", CircleViewSet, basename="circle")
router.register("cycles", CycleViewSet, basename="cycle")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = [
    path("", include(router.urls)),
]
