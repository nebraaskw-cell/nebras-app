from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ParentProfile
from apps.accounts.services import parent_service, registration_service
from apps.attendance.models import AttendanceRecord
from apps.circles.models import Circle, Cycle, Enrollment
from apps.circles.services import enrollment_service
from apps.core.choices import GenderChoices, GovernorateChoices
from apps.study_sessions.models import Session
from apps.study_sessions.services.session_service import generate_sessions_for_cycle


User = get_user_model()
DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Seed demo users, circles, cycles, enrollments, sessions, and report data."

    def handle(self, *args, **options):
        admins = self._create_users("admin", User.Roles.ADMIN, is_staff=True)
        teachers = self._create_users("teacher", User.Roles.TEACHER, is_staff=True)
        students = self._create_users("student", User.Roles.STUDENT)
        parents = self._create_users("parent", User.Roles.PARENT)

        primary_admin = admins[0]
        circles = self._create_circles(teachers)
        cycles = self._create_cycles(circles)
        enrollments = self._create_enrollments(students, cycles, primary_admin)
        self._create_parent_links(parents, students, primary_admin)
        completed_sessions = self._prepare_sessions_and_attendance(enrollments, primary_admin)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(f"Password for every demo account: {DEMO_PASSWORD}")
        self.stdout.write("Admins:   " + ", ".join(user.username for user in admins))
        self.stdout.write("Teachers: " + ", ".join(user.username for user in teachers))
        self.stdout.write("Students: " + ", ".join(user.username for user in students))
        self.stdout.write("Parents:  " + ", ".join(user.username for user in parents))
        self.stdout.write(f"Circles: {len(circles)} | Cycles: {len(cycles)}")
        self.stdout.write(f"Enrollments: {len(enrollments)} | Completed demo sessions: {completed_sessions}")

    def _create_users(self, prefix, role, is_staff=False):
        users = []
        for index in range(1, 6):
            username = f"demo_{prefix}{index}"
            user, _created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": self._first_name(prefix, index),
                    "last_name": "نبراس",
                    "email": f"{username}@example.com",
                    "phone_number": f"+9655{self._phone_suffix(prefix, index)}",
                    "role": role,
                    "registration_status": User.RegistrationStatus.APPROVED,
                    "gender": GenderChoices.MALE if index % 2 else GenderChoices.FEMALE,
                    "governorate": self._governorates()[index - 1],
                    "is_active": True,
                    "is_staff": is_staff,
                    "is_superuser": prefix == "admin" and index == 1,
                },
            )
            user.first_name = self._first_name(prefix, index)
            user.last_name = "نبراس"
            user.email = f"{username}@example.com"
            user.phone_number = f"+9655{self._phone_suffix(prefix, index)}"
            user.role = role
            user.registration_status = User.RegistrationStatus.APPROVED
            user.gender = GenderChoices.MALE if index % 2 else GenderChoices.FEMALE
            user.governorate = self._governorates()[index - 1]
            user.is_active = True
            user.is_staff = is_staff
            if prefix == "admin" and index == 1:
                user.is_superuser = True
            user.set_password(DEMO_PASSWORD)
            user.save()
            users.append(user)
        return users

    def _create_circles(self, teachers):
        circle_data = [
            ("abu_bakr", "حلقة أبي بكر الصديق", GenderChoices.MALE, GovernorateChoices.CAPITAL, "مسجد الدولة الكبير"),
            ("omar", "حلقة عمر بن الخطاب", GenderChoices.MALE, GovernorateChoices.HAWALLI, "مسجد بلال بن رباح"),
            ("othman", "حلقة عثمان بن عفان", GenderChoices.MALE, GovernorateChoices.FARWANIYA, "مسجد الهدى"),
            ("aisha", "حلقة عائشة أم المؤمنين", GenderChoices.FEMALE, GovernorateChoices.MUBARAK_AL_KABEER, "مركز أم المؤمنين"),
            ("fatima", "حلقة فاطمة الزهراء", GenderChoices.FEMALE, GovernorateChoices.AHMADI, "مركز الهدى النسائي"),
        ]
        circles = []
        for index, (name, name_ar, gender, governorate, mosque_name) in enumerate(circle_data):
            circle, _created = Circle.objects.get_or_create(
                name=name,
                defaults={
                    "name_ar": name_ar,
                    "gender": gender,
                    "governorate": governorate,
                    "mosque_name": mosque_name,
                    "location_name": "الكويت",
                    "teacher": teachers[index],
                    "capacity": 25,
                    "is_active": True,
                },
            )
            circle.name_ar = name_ar
            circle.gender = gender
            circle.governorate = governorate
            circle.mosque_name = mosque_name
            circle.location_name = "الكويت"
            circle.teacher = teachers[index]
            circle.capacity = 25
            circle.is_active = True
            circle.save()
            circles.append(circle)
        return circles

    def _create_cycles(self, circles):
        start_date = date.today() - timedelta(days=21)
        cycles = []
        for index, circle in enumerate(circles, start=1):
            cycle, _created = Cycle.objects.get_or_create(
                circle=circle,
                title="دورة ربيع 2026 التجريبية",
                defaults={
                    "start_date": start_date + timedelta(days=index),
                    "status": Cycle.Status.ACTIVE,
                    "notes": "Demo cycle for testing Phase 2 flows.",
                },
            )
            cycle.start_date = start_date + timedelta(days=index)
            cycle.status = Cycle.Status.ACTIVE
            cycle.notes = "Demo cycle for testing Phase 2 flows."
            cycle.save()
            generate_sessions_for_cycle(cycle)
            cycles.append(cycle)
        return cycles

    def _create_enrollments(self, students, cycles, approved_by):
        enrollments = []
        for student, cycle in zip(students, cycles):
            Enrollment.objects.filter(
                student=student,
                status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
            ).exclude(cycle=cycle).update(
                status=Enrollment.Status.WITHDRAWN,
                withdrawn_by=approved_by,
                withdrawn_at=timezone.now(),
            )

            enrollment = Enrollment.objects.filter(student=student, cycle=cycle).first()
            if enrollment is None:
                enrollment = enrollment_service.enroll_student(
                    student=student,
                    cycle=cycle,
                    enrolled_by=approved_by,
                )
            if enrollment.status != Enrollment.Status.ACTIVE:
                enrollment = enrollment_service.approve_enrollment(
                    enrollment=enrollment,
                    approved_by=approved_by,
                )
            enrollments.append(enrollment)
        return enrollments

    def _create_parent_links(self, parents, students, approved_by):
        desired_links = [
            (parents[0], students[0]),
            (parents[0], students[1]),
            (parents[0], students[2]),
            (parents[1], students[3]),
            (parents[2], students[4]),
        ]
        for parent, student in desired_links:
            profile = ParentProfile.objects.filter(parent=parent, student=student).first()
            if profile is None:
                profile = parent_service.request_parent_linking(
                    parent=parent,
                    student=student,
                    notes="Demo parent link.",
                )
            if profile.status == ParentProfile.Status.PENDING:
                parent_service.approve_parent_linking(profile, approved_by=approved_by)

    def _prepare_sessions_and_attendance(self, enrollments, marked_by):
        now = timezone.now()
        completed_sessions = 0
        status_cycle = [
            AttendanceRecord.Status.PRESENT,
            AttendanceRecord.Status.PRESENT,
            AttendanceRecord.Status.LATE,
            AttendanceRecord.Status.ABSENT,
            AttendanceRecord.Status.EXCUSED,
        ]

        for enrollment in enrollments:
            sessions = list(
                Session.objects.filter(cycle=enrollment.cycle)
                .order_by("date", "start_time")[:5]
            )
            for index, session in enumerate(sessions):
                session.status = Session.Status.COMPLETED
                session.completed_at = now
                session.save(update_fields=["status", "completed_at", "updated_at"])
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=enrollment.student,
                    defaults={
                        "status": status_cycle[index % len(status_cycle)],
                        "marked_by": enrollment.cycle.circle.teacher or marked_by,
                    },
                )
                completed_sessions += 1
        return completed_sessions

    def _first_name(self, prefix, index):
        names = {
            "admin": ["مدير", "مشرف", "منسق", "مسؤول", "قائد"],
            "teacher": ["معلم", "مربي", "شيخ", "أستاذ", "مدرب"],
            "student": ["طالب", "حافظ", "متعلم", "دارس", "مجتهد"],
            "parent": ["ولي", "أب", "أم", "متابع", "راعي"],
        }
        return f"{names[prefix][index - 1]} {index}"

    def _governorates(self):
        return [
            GovernorateChoices.CAPITAL,
            GovernorateChoices.HAWALLI,
            GovernorateChoices.FARWANIYA,
            GovernorateChoices.MUBARAK_AL_KABEER,
            GovernorateChoices.AHMADI,
        ]

    def _phone_suffix(self, prefix, index):
        offsets = {
            "admin": 1000,
            "teacher": 2000,
            "student": 3000,
            "parent": 4000,
        }
        return f"{offsets[prefix] + index:06d}"
