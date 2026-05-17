from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.seasons.views import SeasonViewSet, SeasonCircleViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register("seasons", SeasonViewSet, basename="season")
router.register("season_circles", SeasonCircleViewSet, basename="season-circle")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = [
    path("", include(router.urls)),
]
