from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CertificateViewSet,
    CourseEnrollmentViewSet,
    CourseModuleViewSet,
    CourseViewSet,
    LessonCompletionViewSet,
    LessonViewSet,
    ModuleCompletionViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', CourseModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'enrollments', CourseEnrollmentViewSet)
router.register(r'lesson-completions', LessonCompletionViewSet)
router.register(r'module-completions', ModuleCompletionViewSet)
router.register(r'certificates', CertificateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]