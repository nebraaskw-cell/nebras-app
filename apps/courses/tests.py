from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.core.models import SoftDeleteModel

from .models import Course, CourseEnrollment, CourseModule, Lesson


class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='password',
            role=User.Roles.TEACHER
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='password',
            role=User.Roles.STUDENT
        )

    def test_course_creation(self):
        """Test creating a course."""
        course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            title_ar='دورة تجريبية',
            description='A test course',
            capacity=50
        )
        self.assertEqual(course.title, 'Test Course')
        self.assertEqual(course.teacher, self.teacher)
        self.assertEqual(course.status, Course.Status.DRAFT)

    def test_course_enrollment(self):
        """Test course enrollment."""
        course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            capacity=50
        )
        enrollment = CourseEnrollment.objects.create(
            student=self.student,
            course=course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, course)
        self.assertEqual(enrollment.status, CourseEnrollment.Status.PENDING)


class CourseAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='password',
            role=User.Roles.TEACHER
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='password',
            role=User.Roles.STUDENT
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            role=User.Roles.ADMIN
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            title_ar='دورة تجريبية',
            description='A test course',
            capacity=50,
            status=Course.Status.ACTIVE
        )

    def test_course_list_unauthenticated(self):
        """Test course list for unauthenticated users."""
        url = reverse('courses-api:courses-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_list_student(self):
        """Test course list for students."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses-api:courses-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see active courses
        self.assertEqual(len(response.data['results']), 1)

    def test_course_enroll_student(self):
        """Test student enrollment in course."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses-api:courses-enroll', kwargs={'pk': self.course.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check enrollment was created
        enrollment = CourseEnrollment.objects.get(student=self.student, course=self.course)
        self.assertEqual(enrollment.status, CourseEnrollment.Status.PENDING)

    def test_course_create_teacher(self):
        """Test course creation by teacher."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse('courses-api:courses-list')
        data = {
            'title': 'New Course',
            'title_ar': 'دورة جديدة',
            'description': 'A new course',
            'capacity': 30
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_course_create_student_denied(self):
        """Test course creation denied for students."""
        self.client.force_authenticate(user=self.student)
        url = reverse('courses-api:courses-list')
        data = {
            'title': 'New Course',
            'description': 'A new course',
            'capacity': 30
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseModuleAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='password',
            role=User.Roles.TEACHER
        )
        self.course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            capacity=50
        )

    def test_module_creation(self):
        """Test module creation."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse('courses-api:modules-list')
        data = {
            'course': self.course.id,
            'title': 'Test Module',
            'title_ar': 'وحدة تجريبية',
            'description': 'A test module',
            'sequence_order': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseModule.objects.count(), 1)


class LessonAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='password',
            role=User.Roles.TEACHER
        )
        self.course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            capacity=50
        )
        self.module = CourseModule.objects.create(
            course=self.course,
            title='Test Module',
            sequence_order=1
        )

    def test_lesson_creation(self):
        """Test lesson creation."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse('courses-api:lessons-list')
        data = {
            'module': self.module.id,
            'title': 'Test Lesson',
            'title_ar': 'درس تجريبي',
            'content': 'Lesson content',
            'sequence_order': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
