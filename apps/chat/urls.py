from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = "chat"

urlpatterns = [
    path("", LoginRequiredMixin(TemplateView.as_view(template_name="chat/chat_interface.html")), name="interface"),
]
