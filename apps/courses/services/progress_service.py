from django.db.models import Count, Q

from apps.courses.models import CourseEnrollment, Lesson, LessonCompletion, ModuleCompletion


def calculate_course_progress(student, course):
    """
    Calculates the overall progress percentage for a student in a course.

    Returns a dictionary with progress details.
    """
    # Get total lessons in the course
    total_lessons = Lesson.objects.filter(
        module__course=course
    ).count()

    if total_lessons == 0:
        return {
            'progress_percent': 0,
            'completed_lessons': 0,
            'total_lessons': 0,
            'completed_modules': 0,
            'total_modules': course.modules.count(),
        }

    # Get completed lessons by this student
    completed_lessons = LessonCompletion.objects.filter(
        student=student,
        lesson__module__course=course,
        completed_at__isnull=False,
    ).count()

    # Calculate progress percentage
    progress_percent = int((completed_lessons / total_lessons) * 100)

    # Get module completions
    completed_modules = ModuleCompletion.objects.filter(
        student=student,
        module__course=course,
        status=ModuleCompletion.Status.COMPLETED,
    ).count()

    return {
        'progress_percent': progress_percent,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'completed_modules': completed_modules,
        'total_modules': course.modules.count(),
    }


def calculate_module_progress(student, module):
    """
    Calculates the progress percentage for a student in a specific module.

    Returns a dictionary with progress details.
    """
    # Get total lessons in the module
    total_lessons = module.lessons.count()

    if total_lessons == 0:
        return {
            'progress_percent': 0,
            'completed_lessons': 0,
            'total_lessons': 0,
        }

    # Get completed lessons by this student
    completed_lessons = LessonCompletion.objects.filter(
        student=student,
        lesson__module=module,
        completed_at__isnull=False,
    ).count()

    # Calculate progress percentage
    progress_percent = int((completed_lessons / total_lessons) * 100)

    return {
        'progress_percent': progress_percent,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
    }


def update_course_progress(enrollment):
    """
    Updates the progress_percent field on the enrollment based on current completions.

    Returns the updated enrollment.
    """
    progress_data = calculate_course_progress(enrollment.student, enrollment.course)
    enrollment.progress_percent = progress_data['progress_percent']
    enrollment.save(update_fields=['progress_percent'])
    return enrollment


def mark_lesson_complete(student, lesson, time_spent_seconds=0, quiz_score=None):
    """
    Marks a lesson as completed for a student.

    Creates or updates LessonCompletion record.
    Updates module and course progress.

    Returns the LessonCompletion instance.
    """
    completion, created = LessonCompletion.objects.get_or_create(
        student=student,
        lesson=lesson,
        defaults={
            'completed_at': None,
            'time_spent_seconds': time_spent_seconds,
            'quiz_score': quiz_score,
        }
    )

    if not completion.completed_at:
        from django.utils import timezone
        completion.completed_at = timezone.now()
        completion.time_spent_seconds = time_spent_seconds
        if quiz_score is not None:
            completion.quiz_score = quiz_score
        completion.save()

    # Update module completion status
    _update_module_completion_status(student, lesson.module)

    # Update course progress
    enrollment = CourseEnrollment.objects.filter(
        student=student,
        course=lesson.module.course,
        status__in=['active', 'completed']
    ).first()

    if enrollment:
        update_course_progress(enrollment)

    return completion


def _update_module_completion_status(student, module):
    """
    Updates the completion status of a module for a student.
    """
    total_lessons = module.lessons.count()
    completed_lessons = LessonCompletion.objects.filter(
        student=student,
        lesson__module=module,
        completed_at__isnull=False,
    ).count()

    if completed_lessons == 0:
        status = ModuleCompletion.Status.IN_PROGRESS
    elif completed_lessons == total_lessons:
        status = ModuleCompletion.Status.COMPLETED
    else:
        status = ModuleCompletion.Status.IN_PROGRESS

    completion, created = ModuleCompletion.objects.get_or_create(
        student=student,
        module=module,
        defaults={'status': status}
    )

    if not created and completion.status != status:
        from django.utils import timezone
        completion.status = status
        if status == ModuleCompletion.Status.COMPLETED:
            completion.completed_at = timezone.now()
        completion.save()