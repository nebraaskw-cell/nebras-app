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
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'modules', CourseModuleViewSet, basename='modules')
router.register(r'lessons', LessonViewSet, basename='lessons')
router.register(r'enrollments', CourseEnrollmentViewSet, basename='enrollments')
router.register(r'lesson-completions', LessonCompletionViewSet, basename='lesson-completions')
router.register(r'module-completions', ModuleCompletionViewSet, basename='module-completions')
router.register(r'certificates', CertificateViewSet, basename='certificates')

urlpatterns = [
    path('', include(router.urls)),
]