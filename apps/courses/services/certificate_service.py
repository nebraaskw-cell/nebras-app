import uuid

from apps.courses.models import Certificate


def issue_certificate(enrollment):
    """
    Issues a certificate for a completed enrollment.

    Returns the Certificate instance.
    """
    if enrollment.status != enrollment.Status.COMPLETED:
        raise ValueError("Can only issue certificates for completed enrollments.")

    # Check if certificate already exists
    if hasattr(enrollment, 'certificate'):
        return enrollment.certificate

    # Generate unique certificate code
    certificate_code = f"CERT-{enrollment.student.id}-{enrollment.course.id}-{uuid.uuid4().hex[:8].upper()}"

    certificate = Certificate.objects.create(
        enrollment=enrollment,
        student=enrollment.student,
        course=enrollment.course,
        certificate_code=certificate_code,
        is_issued=True,
    )

    return certificate


def get_certificate(student, course):
    """
    Gets the certificate for a student in a specific course.

    Returns Certificate instance or None.
    """
    try:
        return Certificate.objects.get(
            student=student,
            course=course,
            is_issued=True,
        )
    except Certificate.DoesNotExist:
        return None