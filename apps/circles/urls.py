from django.urls import path

from .views import (
    CircleListView,
    CircleCreateView,
    CircleUpdateView,
    CircleDeleteView,
    CircleCloneView,
)

app_name = "circles"

urlpatterns = [
    path("", CircleListView.as_view(), name="list"),
    path("create/", CircleCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", CircleUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", CircleDeleteView.as_view(), name="delete"),
    path("<int:pk>/clone/", CircleCloneView.as_view(), name="clone"),
]
