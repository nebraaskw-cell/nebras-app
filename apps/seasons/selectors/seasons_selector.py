from apps.seasons.models import Season, SeasonCircle, Enrollment


def get_seasons():
    """
    Get all seasons, ordered by start date descending.
    """
    return Season.objects.all()


def get_active_seasons():
    """
    Get seasons currently in ACTIVE status.
    """
    return Season.objects.filter(status=Season.Status.ACTIVE)


def get_open_registration_seasons():
    """
    Get seasons currently open for registrations.
    """
    return Season.objects.filter(status=Season.Status.REGISTRATION_OPEN)


def get_season_circles(season):
    """
    Get all circles participating in a specific season.
    """
    return SeasonCircle.objects.filter(season=season).select_related("circle", "supervisor")


def get_season_enrollments(season):
    """
    Get all enrollments for a specific season.
    """
    return Enrollment.objects.filter(season=season).select_related(
        "student", "season_circle", "season_circle__circle"
    )


def get_student_enrollments(student):
    """
    Get all enrollments for a specific student.
    """
    return Enrollment.objects.filter(student=student).select_related(
        "season", "season_circle", "season_circle__circle"
    )
