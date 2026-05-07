# Architecture

The platform is split into modular Django apps:

- `apps.core`: shared primitives such as base models, choices, permissions, and health checks.
- `apps.accounts`: custom auth user, roles, registration flow, and account APIs.
- `apps.circles`: permanent circles and three-month cycles.
- `apps.study_sessions`: implemented session lifecycle and scheduling workflows.
- `apps.attendance`: implemented attendance tracking and summaries.
- `apps.notifications`: implemented in-app notification orchestration with push boundary.
- `apps.chat`: implemented room/message domain with API endpoints.
- `apps.reports`: implemented reporting APIs and dashboard template.
- `apps.gamification`: implemented points, badges, and reward tracking.
- `apps.logs`: implemented audit logging signals and storage.
- `apps.ai_assistant`: AI integration boundary and scaffolding.
- `apps.ai_evaluation`: AI recitation evaluation boundary and scaffolding.

Current implementation status is beyond Phase 1 and includes delivered features from Phases 2-4.
The current engineering focus is production hardening: reliability, test coverage, observability,
security settings, and UI consistency.

## Service Layer

App-level business operations live under each app's `services/` package. Views handle HTTP/API concerns, serializers handle API transformation, and models keep database structure plus data integrity hooks.

## API-First Foundation

Public and authenticated web pages use Django templates. Mobile-ready APIs live under `/api/v1/`.

## PostgreSQL Readiness

SQLite is the default development database. Set `DB_ENGINE=postgresql` and the related `DB_*` variables to switch environments without changing application code.

## Security Baseline

- Custom user model is configured from the first migration.
- Role fields are indexed for permission checks.
- Pending students are inactive until approved.
- Soft-delete base model is available for domain models.
- CSRF, session cookie, content sniffing, and clickjacking protections are enabled.
