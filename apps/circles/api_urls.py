from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CircleViewSet

router = DefaultRouter()
router.register("circles", CircleViewSet, basename="circle")

urlpatterns = [
    path("", include(router.urls)),
]
