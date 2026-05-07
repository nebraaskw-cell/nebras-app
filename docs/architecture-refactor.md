# Architecture Refactor

This refactor keeps Phase 1 behavior intact while preparing the project for larger SaaS-scale development.

## Layering Rules

- `models.py`: database structure and data integrity.
- `views.py`: HTTP and API request/response handling only.
- `serializers.py`: API validation and representation.
- `services/`: business operations and reusable query boundaries.
- `urls.py` and `api_urls.py`: routing only.

## App Boundaries

- `accounts`: users, roles, registration, approval.
- `circles`: permanent circles and three-month cycles.
- `sessions`: future session lifecycle.
- `attendance`: future session attendance.
- `notifications`: future provider-neutral push notifications.
- `chat`: future global chat.
- `reports`: future report generation and exports.
- `ai_assistant`: future student guidance assistant.
- `ai_evaluation`: future audio recitation evaluation.

## Global Services

The top-level `services/` package is reserved for cross-app orchestration such as cycle archiving snapshots and daily backup exports.
