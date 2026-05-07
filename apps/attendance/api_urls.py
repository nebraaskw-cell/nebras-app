from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceRecordViewSet,
    BulkMarkAttendanceAPIView,
    MarkAttendanceAPIView,
    SessionAttendanceSummaryAPIView,
)

router = DefaultRouter()
router.register("records", AttendanceRecordViewSet, basename="attendance-record")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions/<int:session_id>/mark/",
        MarkAttendanceAPIView.as_view(),
        name="mark-attendance",
    ),
    path(
        "sessions/<int:session_id>/bulk-mark/",
        BulkMarkAttendanceAPIView.as_view(),
        name="bulk-mark-attendance",
    ),
    path(
        "sessions/<int:session_id>/summary/",
        SessionAttendanceSummaryAPIView.as_view(),
        name="attendance-summary",
    ),
]
