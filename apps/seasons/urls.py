from django.urls import path

from .frontend_views import (
    SeasonListView,
    SeasonCreateView,
    SeasonUpdateView,
    SeasonDetailView,
    SeasonDeleteView,
    SeasonCircleCreateView,
    SeasonCircleDeleteView,
    AvailableSeasonsListView,
    StudentEnrollView,
    StudentSelectCircleView,
)

app_name = "seasons"

urlpatterns = [
    # Admin Views
    path("", SeasonListView.as_view(), name="list"),
    path("create/", SeasonCreateView.as_view(), name="create"),
    path("<int:pk>/", SeasonDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", SeasonUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", SeasonDeleteView.as_view(), name="delete"),
    path("<int:season_id>/add-circle/", SeasonCircleCreateView.as_view(), name="circle-create"),
    path("season-circle/<int:pk>/remove/", SeasonCircleDeleteView.as_view(), name="circle-delete"),

    # Student Views
    path("student/available/", AvailableSeasonsListView.as_view(), name="available"),
    path("student/<int:season_id>/enroll/", StudentEnrollView.as_view(), name="student-enroll"),
    path("student/enrollment/<int:pk>/select-circle/", StudentSelectCircleView.as_view(), name="student-select-circle"),
]
