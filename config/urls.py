from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.accounts import api_urls as accounts_api_urls
from apps.ai_assistant import api_urls as ai_assistant_api_urls
from apps.ai_evaluation import api_urls as ai_evaluation_api_urls
from apps.attendance import api_urls as attendance_api_urls
from apps.circles import api_urls as circles_api_urls
from apps.core.views import HealthCheckAPIView, HomeView
from apps.courses import api_urls as courses_api_urls
from apps.notifications import api_urls as notifications_api_urls
from apps.reports import api_urls as reports_api_urls
from apps.seasons import api_urls as seasons_api_urls
from apps.study_sessions import api_urls as sessions_api_urls

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("auth/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("circles/", include("apps.circles.urls")),
    path("seasons/", include("apps.seasons.urls")),
    path("reports/", include("apps.reports.urls")),
    path("api/v1/health/", HealthCheckAPIView.as_view(), name="api-health"),
    path("api/v1/accounts/", include((accounts_api_urls.urlpatterns, "accounts-api"), namespace="accounts-api")),
    path("api/v1/seasons/", include((seasons_api_urls.urlpatterns, "seasons-api"), namespace="seasons-api")),
    path("api/v1/circles/", include((circles_api_urls.urlpatterns, "circles-api"), namespace="circles-api")),
    path("api/v1/sessions/", include((sessions_api_urls.urlpatterns, "sessions-api"), namespace="sessions-api")),
    path("api/v1/attendance/", include((attendance_api_urls.urlpatterns, "attendance-api"), namespace="attendance-api")),
    path(
        "api/v1/notifications/",
        include((notifications_api_urls.urlpatterns, "notifications-api"), namespace="notifications-api"),
    ),
    path("api/v1/reports/", include((reports_api_urls.urlpatterns, "reports-api"), namespace="reports-api")),
    path("api/v1/courses/", include((courses_api_urls.urlpatterns, "courses-api"), namespace="courses-api")),
    path(
        "api/v1/ai/assistant/",
        include((ai_assistant_api_urls.urlpatterns, "ai-assistant-api"), namespace="ai-assistant-api"),
    ),
    path(
        "api/v1/ai/evaluation/",
        include((ai_evaluation_api_urls.urlpatterns, "ai-evaluation-api"), namespace="ai-evaluation-api"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
