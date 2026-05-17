from datetime import date, time

from django.test import TestCase

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord
from apps.attendance.services.attendance_service import mark_attendance
from apps.circles.models import Circle
from apps.seasons.models import Season, SeasonCircle, Enrollment
from apps.study_sessions.models import Session


class AttendanceServiceTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="attendance-teacher",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.other_teacher = User.objects.create_user(
            username="other-attendance-teacher",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.student = User.objects.create_user(
            username="attendance-student",
            password="pass12345",
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        self.circle = Circle.objects.create(
            name="Circle C",
            name_ar="الدائرة ج",
            gender="male",
            governorate="capital",
            teacher=self.teacher,
            status=Circle.Status.OPEN,
        )
        self.season = Season.objects.create(
            title="Evening Tajweed",
            start_date=date.today(),
            end_date=date.today() + date.resolution * 90,
            status=Season.Status.ACTIVE,
        )
        self.cycle = SeasonCircle.objects.create(
            season=self.season,
            circle=self.circle,
            supervisor=self.teacher,
            capacity=25,
        )
        self.session = Session.objects.create(
            cycle=self.cycle,
            title="Attendance Session",
            date=self.season.start_date,
            start_time=time(16, 0),
            end_time=time(18, 0),
            status=Session.Status.ACTIVE,
        )

    def test_mark_attendance_rejects_when_teacher_is_not_assigned(self):
        Enrollment.objects.create(
            student=self.student,
            season=self.season,
            season_circle=self.cycle,
            status=Enrollment.Status.ACTIVE,
        )

        with self.assertRaisesMessage(ValueError, "not the assigned teacher"):
            mark_attendance(
                session=self.session,
                student=self.student,
                status=AttendanceRecord.Status.PRESENT,
                marked_by=self.other_teacher,
            )

    def test_mark_attendance_rejects_when_student_is_not_enrolled(self):
        with self.assertRaisesMessage(ValueError, "does not have an active enrollment"):
            mark_attendance(
                session=self.session,
                student=self.student,
                status=AttendanceRecord.Status.PRESENT,
                marked_by=self.teacher,
            )
