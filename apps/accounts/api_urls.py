from django.urls import path

from .views import (
    ApproveStudentAPIView,
    MeAPIView,
    PendingStudentListAPIView,
    StudentRegistrationAPIView,
    ParentLinkRequestAPIView,
    PendingParentLinkListAPIView,
    ApproveParentLinkAPIView,
)

urlpatterns = [
    path("me/", MeAPIView.as_view(), name="me"),
    path("register/student/", StudentRegistrationAPIView.as_view(), name="student-register"),
    path("students/pending/", PendingStudentListAPIView.as_view(), name="pending-students"),
    path("students/<int:pk>/approve/", ApproveStudentAPIView.as_view(), name="approve-student"),
    path("parents/link-request/", ParentLinkRequestAPIView.as_view(), name="parent-link-request"),
    path("parents/pending/", PendingParentLinkListAPIView.as_view(), name="pending-parents"),
    path("parents/<int:pk>/approve/", ApproveParentLinkAPIView.as_view(), name="approve-parent"),
]

