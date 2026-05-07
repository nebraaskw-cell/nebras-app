# Halaqat Nebras - حلقات نبراس لحفظ السنة النبوية

Production-oriented Django + DRF educational platform for managing Sunnah memorization circles in Kuwait.

## Current Scope

This repository currently implements:

- Phase 1 core: user roles, registration approval, circles, cycles, admin, template pages
- Phase 2 delivery: sessions lifecycle, attendance flows, enrollment lifecycle, notifications APIs
- Phase 3 delivery: chat domain, reporting dashboards/APIs, parent linking workflows
- Phase 4 partial delivery: gamification, activity logs, archiving and backup utilities
- Phase 5 scaffolding: AI assistant and AI evaluation integration boundaries (structure only)

The project is now in a **pre-production hardening stage** where reliability, UI consistency,
test coverage, and operational readiness are the main priorities.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Web: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API health: http://127.0.0.1:8000/api/v1/health/

## Phase Roadmap

1. Phase 1: Users, roles, circles, cycles, basic auth, admin. (implemented)
2. Phase 2: Sessions, attendance, enrollment, notifications. (implemented)
3. Phase 3: Global chat, reports, parent linking. (implemented)
4. Phase 4: Archiving snapshots, gamification, activity logs, backups. (partially implemented)
5. Phase 5: AI service structure only. (scaffolded)

