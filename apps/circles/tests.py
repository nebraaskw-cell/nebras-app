from datetime import date

from django.test import TestCase

from apps.accounts.models import User
from apps.circles.models import Circle, Cycle, Enrollment
from apps.circles.services.cycle_service import calculate_cycle_end_date
from apps.circles.services.enrollment_service import enroll_student


class EnrollmentServiceTests(TestCase):
    def setUp(self):
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
            mosque_name="Al-Fajr Mosque",
            capacity=2,
            teacher=self.teacher,
            is_active=True,
        )
        self.cycle = Cycle.objects.create(
            circle=self.circle,
            title="Summer Quran Program",
            start_date=date.today(),
            end_date=calculate_cycle_end_date(date.today()),
            status=Cycle.Status.ACTIVE,
        )

    def test_enroll_student_creates_pending_enrollment(self):
        enrollment = enroll_student(
            student=self.student,
            cycle=self.cycle,
            enrolled_by=self.teacher,
        )

        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.cycle, self.cycle)

    def test_enroll_student_rejects_when_cycle_is_full(self):
        other_student = User.objects.create_user(
            username="other-student",
            password="pass12345",
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )
        third_student = User.objects.create_user(
            username="third-student",
            password="pass12345",
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )

        Enrollment.objects.create(
            student=other_student,
            cycle=self.cycle,
            status=Enrollment.Status.ACTIVE,
        )
        Enrollment.objects.create(
            student=third_student,
            cycle=self.cycle,
            status=Enrollment.Status.PENDING,
        )

        with self.assertRaisesMessage(ValueError, "full"):
            enroll_student(
                student=self.student,
                cycle=self.cycle,
                enrolled_by=self.teacher,
            )

    def test_enroll_student_rejects_when_student_has_existing_enrollment(self):
        Enrollment.objects.create(
            student=self.student,
            cycle=self.cycle,
            status=Enrollment.Status.ACTIVE,
        )

        with self.assertRaisesMessage(ValueError, "already has a Active enrollment"):
            enroll_student(
                student=self.student,
                cycle=self.cycle,
                enrolled_by=self.teacher,
            )

    def test_enroll_student_rejects_when_cycle_is_completed(self):
        self.cycle.status = Cycle.Status.COMPLETED
        self.cycle.save(update_fields=["status"])

        with self.assertRaisesMessage(ValueError, "completed or archived"):
            enroll_student(
                student=self.student,
                cycle=self.cycle,
                enrolled_by=self.teacher,
            )
