from django.urls import path
from .views import CircleReportAPIView, StudentPerformanceAPIView, RegistrationAnalyticsAPIView

urlpatterns = [
    path("circles/<int:pk>/", CircleReportAPIView.as_view(), name="circle-report"),
    path("students/<int:pk>/", StudentPerformanceAPIView.as_view(), name="student-report"),
    path("analytics/registrations/", RegistrationAnalyticsAPIView.as_view(), name="registration-analytics"),
]
