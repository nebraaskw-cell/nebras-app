from django.urls import path

from .views import DashboardView, StudentRegistrationCompleteView, StudentRegistrationView

app_name = "accounts"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("register/student/", StudentRegistrationView.as_view(), name="student-register"),
    path("register/student/complete/", StudentRegistrationCompleteView.as_view(), name="student-register-complete"),
]

