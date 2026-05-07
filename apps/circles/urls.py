from django.urls import path

from .views import CircleListView, CycleListView

app_name = "circles"

urlpatterns = [
    path("", CircleListView.as_view(), name="list"),
    path("cycles/", CycleListView.as_view(), name="cycles"),
]

