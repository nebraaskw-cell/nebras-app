from django.utils import timezone
from apps.circles.models import Cycle, Enrollment

def archive_cycle(cycle: Cycle, user):
    """
    Orchestrates the archiving of a cycle.
    
    1. Marks the cycle status as ARCHIVED.
    2. Marks all active enrollments as COMPLETED.
    3. Sets archived_at and audit info.
    """
    if cycle.status == Cycle.Status.ARCHIVED:
        return cycle
        
    # Mark cycle as archived
    cycle.status = Cycle.Status.ARCHIVED
    cycle.archived_at = timezone.now()
    cycle.save()
    
    # Update active enrollments to completed
    Enrollment.objects.filter(
        cycle=cycle,
        status=Enrollment.Status.ACTIVE
    ).update(
        status=Enrollment.Status.COMPLETED
    )
    
    return cycle

def get_archived_stats(cycle: Cycle):
    """
    Retrieves a summary of the cycle results at the time of archiving.
    (This is a helper for the snapshot logic).
    """
    return {
        "cycle_id": cycle.id,
        "title": cycle.title,
        "circle": cycle.circle.name_ar,
        "archived_at": cycle.archived_at.isoformat() if cycle.archived_at else None,
        "student_count": Enrollment.objects.filter(cycle=cycle).count(),
        "completion_count": Enrollment.objects.filter(cycle=cycle, status=Enrollment.Status.COMPLETED).count(),
    }
