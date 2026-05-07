# Halaqat Nebras Project Tree

Updated after Phase 2 implementation.

Generated/local files are intentionally excluded from the detailed tree:

- `.venv/`
- `__pycache__/`
- `*.pyc`
- `db.sqlite3`
- `media/` contents
- `staticfiles/`

```text
nebras-sunnah/
|-- .env.example
|-- .gitignore
|-- PROJECT_TREE.md
|-- schema.prisma
|-- README.md
|-- manage.py
|-- requirements.txt
|-- apps/
|   |-- __init__.py
|   |-- accounts/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- forms.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- signals.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |   |-- 0001_initial.py
|   |   |   `-- 0002_alter_user_registration_status.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       |-- registration_service.py
|   |       `-- user_policy.py
|   |-- ai_assistant/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       `-- assistant_service.py
|   |-- ai_evaluation/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       `-- evaluation_service.py
|   |-- attendance/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |   `-- 0001_initial.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       `-- attendance_service.py
|   |-- chat/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       `-- global_chat_service.py
|   |-- circles/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |   |-- 0001_initial.py
|   |   |   |-- 0002_alter_cycle_end_date.py
|   |   |   `-- 0003_enrollment.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       |-- cycle_service.py
|   |       |-- enrollment_service.py
|   |       `-- query_service.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- choices.py
|   |   |-- models.py
|   |   |-- permissions.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       `-- __init__.py
|   |-- notifications/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |   `-- 0001_initial.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       |-- notification_service.py
|   |       `-- push_service.py
|   |-- reports/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- __init__.py
|   |       `-- generation_service.py
|   `-- study_sessions/
|       |-- __init__.py
|       |-- admin.py
|       |-- api_urls.py
|       |-- apps.py
|       |-- models.py
|       |-- serializers.py
|       |-- signals.py
|       |-- urls.py
|       |-- views.py
|       |-- migrations/
|       |   |-- __init__.py
|       |   `-- 0001_initial.py
|       `-- services/
|           |-- __init__.py
|           `-- session_service.py
|-- config/
|   |-- __init__.py
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- docs/
|   |-- architecture.md
|   |-- architecture-refactor.md
|   `-- phase-1.md
|-- media/
|-- services/
|   |-- __init__.py
|   |-- archiving.py
|   `-- backups.py
|-- static/
|   `-- css/
|       `-- site.css
`-- templates/
    |-- home.html
    |-- accounts/
    |   |-- dashboard.html
    |   |-- login.html
    |   |-- register.html
    |   `-- register_complete.html
    |-- base/
    |   `-- base.html
    `-- circles/
        |-- cycles.html
        `-- list.html
```

