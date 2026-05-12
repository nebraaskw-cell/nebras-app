from datetime import date, time

from django.test import TestCase

from apps.accounts.models import User
from apps.circles.models import Circle, Cycle
from apps.circles.services.cycle_service import calculate_cycle_end_date
from apps.study_sessions.models import Session
from apps.study_sessions.services.session_service import start_session


class SessionServiceTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="session-teacher",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.other_teacher = User.objects.create_user(
            username="other-teacher",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.circle = Circle.objects.create(
            name="Circle B",
            name_ar="الدائرة ب",
            gender="male",
            governorate="capital",
            mosque_name="Al-Nour Mosque",
            teacher=self.teacher,
            is_active=True,
        )
        self.cycle = Cycle.objects.create(
            circle=self.circle,
            title="Weekend Hifz",
            start_date=date.today(),
            end_date=calculate_cycle_end_date(date.today()),
            status=Cycle.Status.ACTIVE,
        )
        self.session = Session.objects.create(
            cycle=self.cycle,
            title="Session 1",
            date=self.cycle.start_date,
            start_time=time(16, 0),
            end_time=time(18, 0),
            status=Session.Status.SCHEDULED,
        )

    def test_start_session_allows_assigned_teacher(self):
        session = start_session(self.session, started_by=self.teacher)

        self.assertEqual(session.status, Session.Status.ACTIVE)
        self.assertIsNotNone(session.started_at)

    def test_start_session_rejects_unassigned_teacher(self):
        with self.assertRaisesMessage(ValueError, "assigned to this circle"):
            start_session(self.session, started_by=self.other_teacher)
