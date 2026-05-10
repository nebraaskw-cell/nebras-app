from django.urls import path
from .views import (
    CircleReportAPIView,
    CircleReportExcelAPIView,
    RegistrationAnalyticsAPIView,
    RegistrationAnalyticsExcelAPIView,
    StudentPerformanceAPIView,
    StudentPerformanceExcelAPIView,
)

urlpatterns = [
    path("circles/<int:pk>/excel/", CircleReportExcelAPIView.as_view(), name="circle-report-excel"),
    path("circles/<int:pk>/", CircleReportAPIView.as_view(), name="circle-report"),
    path("students/<int:pk>/excel/", StudentPerformanceExcelAPIView.as_view(), name="student-report-excel"),
    path("students/<int:pk>/", StudentPerformanceAPIView.as_view(), name="student-report"),
    path("analytics/registrations/excel/", RegistrationAnalyticsExcelAPIView.as_view(), name="registration-analytics-excel"),
    path("analytics/registrations/", RegistrationAnalyticsAPIView.as_view(), name="registration-analytics"),
]
