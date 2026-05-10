# Halaqat Nebras Project Tree

Updated after chat removal, WhatsApp scaffold, parent multi-student linking,
report Excel exports, and demo-data seeding.

Generated/local files are intentionally excluded:

- `.venv/`
- `venv/`
- `__pycache__/`
- `*.pyc`
- `db.sqlite3`
- `media/` contents
- `staticfiles/`

```text
nebras-app/
|-- .env.example
|-- .gitignore
|-- PROJECT_TREE.md
|-- README.md
|-- manage.py
|-- requirements.txt
|-- test_endpoints.py
|-- apps/
|   |-- accounts/
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
|   |   |   |-- 0001_initial.py
|   |   |   |-- 0002_alter_user_registration_status.py
|   |   |   |-- 0003_add_parent_profile.py
|   |   |   |-- 0004_alter_parentprofile_parent.py
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- parent_service.py
|   |       |-- registration_service.py
|   |       |-- user_policy.py
|   |       `-- __init__.py
|   |-- ai_assistant/
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
|   |       |-- assistant_service.py
|   |       `-- __init__.py
|   |-- ai_evaluation/
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
|   |       |-- evaluation_service.py
|   |       `-- __init__.py
|   |-- attendance/
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- attendance_service.py
|   |       `-- __init__.py
|   |-- circles/
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- signals.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py
|   |   |   |-- 0002_alter_cycle_end_date.py
|   |   |   |-- 0003_enrollment.py
|   |   |   |-- 0004_add_enrollment_withdrawal_audit.py
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- cycle_service.py
|   |       |-- enrollment_service.py
|   |       |-- query_service.py
|   |       `-- __init__.py
|   |-- core/
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- choices.py
|   |   |-- models.py
|   |   |-- permissions.py
|   |   |-- views.py
|   |   |-- management/
|   |   |   `-- commands/
|   |   |       |-- backup_system.py
|   |   |       |-- seed_demo_data.py
|   |   |       `-- __init__.py
|   |   |-- migrations/
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       `-- __init__.py
|   |-- gamification/
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- gamification_service.py
|   |       `-- __init__.py
|   |-- logs/
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- signals.py
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py
|   |   |   `-- __init__.py
|   |-- notifications/
|   |   |-- admin.py
|   |   |-- api_urls.py
|   |   |-- apps.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py
|   |   |   `-- __init__.py
|   |   `-- services/
|   |       |-- notification_service.py
|   |       |-- push_service.py
|   |       |-- whatsapp_service.py
|   |       `-- __init__.py
|   |-- reports/
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
|   |       |-- generation_service.py
|   |       `-- __init__.py
|   `-- study_sessions/
|       |-- admin.py
|       |-- api_urls.py
|       |-- apps.py
|       |-- models.py
|       |-- serializers.py
|       |-- signals.py
|       |-- urls.py
|       |-- views.py
|       |-- migrations/
|       |   |-- 0001_initial.py
|       |   `-- __init__.py
|       `-- services/
|           |-- session_service.py
|           `-- __init__.py
|-- config/
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   `-- __init__.py
|-- docs/
|   |-- architecture.md
|   |-- architecture-refactor.md
|   `-- phase-1.md
|-- services/
|   |-- archiving.py
|   |-- backups.py
|   `-- __init__.py
|-- static/
|   |-- css/
|   |   `-- site.css
|   `-- js/
|       |-- dashboard.js
|       |-- parent_dashboard.js
|       `-- reports.js
`-- templates/
    |-- home.html
    |-- accounts/
    |   |-- admin_dashboard.html
    |   |-- dashboard.html
    |   |-- login.html
    |   |-- parent_dashboard.html
    |   |-- register.html
    |   |-- register_complete.html
    |   |-- student_dashboard.html
    |   `-- teacher_dashboard.html
    |-- base/
    |   `-- base.html
    |-- circles/
    |   |-- cycles.html
    |   `-- list.html
    |-- components/
    |   |-- empty_state.html
    |   |-- kpi_card.html
    |   `-- page_header.html
    `-- reports/
        `-- reports.html
```
