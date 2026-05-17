# Halaqat Nebras - حلقات نبراس لحفظ السنة النبوية

Production-oriented Django + DRF educational platform for managing Sunnah memorization circles in Kuwait.

## Current Scope

This repository currently implements:

- **Phase 1 (Core Foundations):** User roles (Student, Teacher, Parent, Admin), registration approval pipelines, circle/cycle models, admin panels, and standard layout template pages.
- **Phase 2 (Sessions & Attendance):** Study sessions lifecycle, automated attendance tracking workflows, enrollment lifecycle states, and notification backend APIs.
- **Phase 3 (Reporting & Parent Portals):** Rich dashboard reporting (including Excel exports), multi-student parent linking workflows, and notification provider scaffolds.
- **Phase 4 (Gamification, Backups, & Courses):** Gamification modules (points, level progression, badges), comprehensive audit logs, automated database backup scripts, cycle archiving snapshots, and the full Courses module with dynamic progress tracking and certificate generation.
- **Phase 5 (AI Guidance & Evaluation):** AI Assistant for Islamic educational guidance and automated AI Evaluation of student recitation transcripts.

The project is in its **pre-production hardening stage** where reliability, UI consistency, test coverage, and operational readiness are prioritized.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Add OPENAI_API_KEY to .env for AI features
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Open:

- Web: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- API health: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)

## Phase Roadmap

1. **Phase 1: Users, roles, circles, cycles, basic auth, admin.** (implemented)
2. **Phase 2: Sessions, attendance, enrollment, notifications.** (implemented)
3. **Phase 3: Reports, parent linking, notifications.** (implemented)
4. **Phase 4: Snapshot archiving, gamification, activity logs, database backups, and courses.** (implemented)
5. **Phase 5: AI assistant & AI evaluation integration.** (implemented)
