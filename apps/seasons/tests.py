from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.circles.models import Circle
from apps.seasons.models import Season, SeasonCircle, Enrollment, SeasonSnapshot
from apps.seasons.services import enrollment_service
from apps.seasons.services.season_archive_service import archive_season


class SeasonArchitectureTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin-user",
            password="pass12345",
            role=User.Roles.ADMIN,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.teacher = User.objects.create_user(
            username="teacher-user",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.student = User.objects.create_user(
            username="student-user",
            password="pass12345",
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.circle = Circle.objects.create(
            name="Circle A",
            name_ar="الدائرة أ",
            gender="male",
            governorate="capital",
            teacher=self.teacher,
            status=Circle.Status.OPEN,
        )
        self.season = Season.objects.create(
            title="Summer Season 2026",
            start_date=date.today(),
            status=Season.Status.REGISTRATION_OPEN,
        )
        self.season_circle = SeasonCircle.objects.create(
            season=self.season,
            circle=self.circle,
            supervisor=self.teacher,
            capacity=25,
        )

    def test_student_enrollment_in_open_registration_season(self):
        # 1. Enrolls in season first (Status is PENDING)
        enrollment = enrollment_service.enroll_student_in_season(
            student=self.student,
            season=self.season,
            enrolled_by=self.teacher,
        )
        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)
        self.assertIsNone(enrollment.season_circle)

        # 2. Assigns a circle
        enrollment = enrollment_service.assign_circle_to_enrollment(
            enrollment=enrollment,
            season_circle=self.season_circle,
        )
        self.assertEqual(enrollment.season_circle, self.season_circle)

        # 3. Approves enrollment
        enrollment = enrollment_service.approve_enrollment(
            enrollment=enrollment,
            approved_by=self.admin,
        )
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)

    def test_student_enrollment_rejects_when_not_registration_open(self):
        closed_season = Season.objects.create(
            title="Closed Season 2026",
            start_date=date.today(),
            status=Season.Status.CLOSED,
        )
        with self.assertRaises(ValidationError):
            enrollment_service.enroll_student_in_season(
                student=self.student,
                season=closed_season,
            )

    def test_student_enrollment_rejects_with_mismatched_circle(self):
        other_season = Season.objects.create(
            title="Other Season 2026",
            start_date=date.today(),
            status=Season.Status.REGISTRATION_OPEN,
        )
        other_season_circle = SeasonCircle.objects.create(
            season=other_season,
            circle=self.circle,
        )
        enrollment = enrollment_service.enroll_student_in_season(
            student=self.student,
            season=self.season,
        )
        # Rejects choosing circle not linked to this season
        with self.assertRaises(ValidationError):
            enrollment_service.assign_circle_to_enrollment(
                enrollment=enrollment,
                season_circle=other_season_circle,
            )

    def test_archive_season_generates_snapshot(self):
        enrollment = enrollment_service.enroll_student_in_season(
            student=self.student,
            season=self.season,
        )
        enrollment = enrollment_service.assign_circle_to_enrollment(
            enrollment=enrollment,
            season_circle=self.season_circle,
        )
        enrollment = enrollment_service.approve_enrollment(
            enrollment=enrollment,
            approved_by=self.admin,
        )

        # Archive the season (must be active or closed to archive)
        self.season.status = Season.Status.ACTIVE
        self.season.save()
        archive_season(self.season, self.admin)

        self.assertEqual(self.season.status, Season.Status.ARCHIVED)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.COMPLETED)

        # Check snapshot exists
        snapshot = SeasonSnapshot.objects.filter(season=self.season).first()
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.data["title"], "Summer Season 2026")
        self.assertEqual(snapshot.data["total_students"], 1)
        self.assertEqual(len(snapshot.data["circles"]), 1)
        self.assertEqual(snapshot.data["circles"][0]["name_ar"], "الدائرة أ")
