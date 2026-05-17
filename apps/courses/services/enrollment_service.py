from django.utils import timezone

from apps.courses.models import CourseEnrollment


def _validate_student(student):
    """Guard: only user with role=student can be enrolled."""
    if getattr(student, "role", None) != "student":
        raise ValueError("Only student users can be enrolled.")


def enroll_student(student, course, enrolled_by=None):
    """
    Creates a PENDING enrollment for the student in the given course.

    Rules enforced:
    - User must have role=student.
    - Student must have NO existing PENDING or ACTIVE enrollment
      in the same course. A student can enroll in multiple courses.
    - The target course cannot be completed or archived.
    - The target course must have available capacity.

    Raises ValueError if any conflict exists.
    Returns the new CourseEnrollment instance.
    """
    _validate_student(student)

    if course.status in [course.Status.COMPLETED, course.Status.ARCHIVED]:
        raise ValueError(
            "Cannot enroll in a course that is completed or archived."
        )

    capacity_usage = CourseEnrollment.objects.filter(
        course=course,
        status__in=[CourseEnrollment.Status.PENDING, CourseEnrollment.Status.ACTIVE],
    ).count()
    if capacity_usage >= course.capacity:
        raise ValueError(
            "This course is full and cannot accept additional enrollments."
        )

    conflicting = CourseEnrollment.objects.filter(
        student=student,
        course=course,
        status__in=[CourseEnrollment.Status.PENDING, CourseEnrollment.Status.ACTIVE],
    ).first()

    if conflicting:
        raise ValueError(
            f"Student already has a {conflicting.get_status_display()} enrollment "
            f"in '{course.title_ar}'. "
            "Cannot enroll twice in the same course."
        )

    return CourseEnrollment.objects.create(
        student=student,
        course=course,
        status=CourseEnrollment.Status.PENDING,
    )


def approve_enrollment(enrollment, approved_by):
    """
    Transitions a PENDING enrollment to ACTIVE.

    Rules enforced:
    - User on the enrollment must have role=student.

    Returns the updated CourseEnrollment instance.
    """
    _validate_student(enrollment.student)

    now = timezone.now()

    enrollment.status = CourseEnrollment.Status.ACTIVE
    enrollment.approved_by = approved_by
    enrollment.approved_at = now
    enrollment.save()

    return enrollment


def withdraw_enrollment(enrollment, withdrawn_by):
    """
    Transitions any enrollment to WITHDRAWN.

    Returns the updated CourseEnrollment instance.
    """
    now = timezone.now()

    enrollment.status = CourseEnrollment.Status.WITHDRAWN
    enrollment.withdrawn_by = withdrawn_by
    enrollment.withdrawn_at = now
    enrollment.save()

    return enrollment


def complete_enrollment(enrollment, grade=None):
    """
    Marks an enrollment as COMPLETED and issues a certificate.

    Returns the updated CourseEnrollment instance.
    """
    from .certificate_service import issue_certificate

    now = timezone.now()

    enrollment.status = CourseEnrollment.Status.COMPLETED
    enrollment.completion_date = now
    if grade is not None:
        enrollment.grade = grade
    enrollment.progress_percent = 100
    enrollment.save()

    # Issue certificate
    issue_certificate(enrollment)

    return enrollment