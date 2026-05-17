from apps.courses.models import Course, CourseEnrollment


def create_course(teacher, data):
    """
    Creates a new course.

    Returns the Course instance.
    """
    course = Course.objects.create(
        teacher=teacher,
        **data
    )
    return course


def get_course_progress(student, course):
    """
    Gets the progress summary for a student in a course.

    Returns a dictionary with progress details.
    """
    from .progress_service import calculate_course_progress
    return calculate_course_progress(student, course)


def get_student_enrollments(student, status_filter=None):
    """
    Gets all enrollments for a student.

    Returns QuerySet of CourseEnrollment.
    """
    queryset = CourseEnrollment.objects.filter(student=student)

    if status_filter:
        if isinstance(status_filter, list):
            queryset = queryset.filter(status__in=status_filter)
        else:
            queryset = queryset.filter(status=status_filter)

    return queryset.select_related('course', 'course__teacher')


def get_teacher_courses(teacher, status_filter=None):
    """
    Gets all courses for a teacher.

    Returns QuerySet of Course.
    """
    queryset = Course.objects.filter(teacher=teacher)

    if status_filter:
        if isinstance(status_filter, list):
            queryset = queryset.filter(status__in=status_filter)
        else:
            queryset = queryset.filter(status=status_filter)

    return queryset.prefetch_related('modules', 'enrollments')


def get_active_courses():
    """
    Gets all active courses available for enrollment.

    Returns QuerySet of Course.
    """
    return Course.objects.filter(
        status=Course.Status.ACTIVE
    ).select_related('teacher').prefetch_related('modules')


def complete_course(enrollment):
    """
    Marks a course as completed for a student.

    Issues certificate and updates enrollment.

    Returns the updated enrollment.
    """
    from .enrollment_service import complete_enrollment
    return complete_enrollment(enrollment)