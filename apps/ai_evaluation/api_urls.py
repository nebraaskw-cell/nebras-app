from django.urls import path

from .views import EvaluationAPIView

urlpatterns = [
    path("evaluate/", EvaluationAPIView.as_view(), name="evaluation"),
]

