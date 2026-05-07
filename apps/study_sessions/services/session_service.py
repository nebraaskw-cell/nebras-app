from datetime import timedelta

from django.utils import timezone

from apps.study_sessions.models import Session


VALID_TRANSITIONS = {
    "scheduled": ["active", "cancelled"],
    "active": ["completed", "cancelled"],
}

SESSION_WEEKDAYS = {1, 5}


def generate_sessions_for_cycle(cycle):
    """
    Auto-generates 2 sessions per week (Sat + Tue)
    for the full cycle duration.
    Uses cycle.default_session_start_time and end_time.
    Sets is_auto_generated=True.
    Skips generation if sessions already exist for this cycle.
    Returns count of sessions created.
    """
    if Session.objects.filter(cycle=cycle).exists():
        return 0

    sessions = []
    current_date = cycle.start_date
    while current_date and current_date < cycle.end_date:
        if current_date.weekday() in SESSION_WEEKDAYS:
            sessions.append(
                Session(
                    cycle=cycle,
                    title=f"{cycle.title} - {current_date}",
                    date=current_date,
                    start_time=cycle.default_session_start_time,
                    end_time=cycle.default_session_end_time,
                    status=Session.Status.SCHEDULED,
                    is_auto_generated=True,
                )
            )
        current_date += timedelta(days=1)

    Session.objects.bulk_create(sessions)
    return len(sessions)


def _validate_transition(session, next_status):
    allowed_statuses = VALID_TRANSITIONS.get(session.status, [])
    if next_status not in allowed_statuses:
        raise ValueError(f"Invalid session transition: {session.status} -> {next_status}")


def start_session(session, started_by):
    """
    Transitions session SCHEDULED -> ACTIVE.
    Raises ValueError if another session in same cycle is ACTIVE.
    Raises ValueError if transition is invalid.
    Sets started_at = now().
    """
    _validate_transition(session, Session.Status.ACTIVE)
    if Session.objects.filter(cycle=session.cycle, status=Session.Status.ACTIVE).exclude(pk=session.pk).exists():
        raise ValueError("Another session in this cycle is already active.")
    session.status = Session.Status.ACTIVE
    session.started_at = timezone.now()
    session.save(update_fields=["status", "started_at", "updated_at"])
    return session


def complete_session(session, completed_by):
    """
    Transitions session ACTIVE -> COMPLETED.
    Sets completed_at = now().
    """
    _validate_transition(session, Session.Status.COMPLETED)
    session.status = Session.Status.COMPLETED
    session.completed_at = timezone.now()
    session.save(update_fields=["status", "completed_at", "updated_at"])
    return session


def cancel_session(session, cancelled_by):
    """
    Transitions SCHEDULED or ACTIVE -> CANCELLED.
    """
    _validate_transition(session, Session.Status.CANCELLED)
    session.status = Session.Status.CANCELLED
    session.save(update_fields=["status", "updated_at"])
    return session
