from django.urls import path

from .views import AssistantPromptAPIView

urlpatterns = [
    path("prompt/", AssistantPromptAPIView.as_view(), name="assistant-prompt"),
]

