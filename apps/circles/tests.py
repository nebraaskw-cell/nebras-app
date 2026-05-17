from django.test import TestCase
from apps.accounts.models import User
from apps.circles.models import Circle


class CircleTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher-user",
            password="pass12345",
            role=User.Roles.TEACHER,
            registration_status=User.RegistrationStatus.APPROVED,
            is_active=True,
        )

    def test_create_circle(self):
        circle = Circle.objects.create(
            name="Circle A",
            name_ar="الدائرة أ",
            gender="male",
            governorate="capital",
            teacher=self.teacher,
            status=Circle.Status.OPEN,
        )
        self.assertEqual(circle.name, "Circle A")
        self.assertEqual(circle.teacher, self.teacher)
        self.assertEqual(circle.gender, "male")
        self.assertEqual(circle.status, Circle.Status.OPEN)
