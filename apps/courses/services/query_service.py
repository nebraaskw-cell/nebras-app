from apps.courses.models import Course, CourseEnrollment


def get_courses():
    """
    Gets all courses with related data.

    Returns QuerySet of Course.
    """
    return Course.objects.select_related('teacher').prefetch_related('modules')


def get_course_enrollments():
    """
    Gets all course enrollments with related data.

    Returns QuerySet of CourseEnrollment.
    """
    return CourseEnrollment.objects.select_related(
        'student', 'course', 'course__teacher', 'approved_by'
    )


def get_active_course_enrollments():
    """
    Gets all active course enrollments.

    Returns QuerySet of CourseEnrollment.
    """
    return get_course_enrollments().filter(status=CourseEnrollment.Status.ACTIVE)


def get_pending_course_enrollments():
    """
    Gets all pending course enrollments.

    Returns QuerySet of CourseEnrollment.
    """
    return get_course_enrollments().filter(status=CourseEnrollment.Status.PENDING)


def get_student_course_enrollments(student):
    """
    Gets all course enrollments for a specific student.

    Returns QuerySet of CourseEnrollment.
    """
    return CourseEnrollment.objects.filter(
        student=student
    ).select_related('course', 'course__teacher')


def get_course_student_enrollments(course):
    """
    Gets all enrollments for a specific course.

    Returns QuerySet of CourseEnrollment.
    """
    return CourseEnrollment.objects.filter(
        course=course
    ).select_related('student')