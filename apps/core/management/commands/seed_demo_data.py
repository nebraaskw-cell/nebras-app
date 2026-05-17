from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ParentProfile
from apps.accounts.services import parent_service, registration_service
from apps.attendance.models import AttendanceRecord
from apps.circles.models import Circle
from apps.seasons.models import Season, SeasonCircle, Enrollment
from apps.seasons.services import enrollment_service
from apps.core.choices import GenderChoices, GovernorateChoices
from apps.study_sessions.models import Session
from apps.study_sessions.services.session_service import generate_sessions_for_cycle


User = get_user_model()
DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Seed demo users, seasons, circles, enrollments, sessions, and report data."

    def handle(self, *args, **options):
        admins = self._create_users("admin", User.Roles.ADMIN, is_staff=True)
        teachers = self._create_users("teacher", User.Roles.TEACHER, is_staff=True)
        students = self._create_users("student", User.Roles.STUDENT)
        parents = self._create_users("parent", User.Roles.PARENT)

        primary_admin = admins[0]
        circles = self._create_circles(teachers)
        
        # 1. Create global Season
        season = self._create_season()
        
        # 2. Create SeasonCircles
        season_circles = self._create_season_circles(season, circles)
        
        # 3. Create Season Enrollments and assign to circles
        enrollments = self._create_enrollments(students, season, season_circles, primary_admin)
        
        self._create_parent_links(parents, students, primary_admin)
        
        completed_sessions = self._prepare_sessions_and_attendance(enrollments, primary_admin)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(f"Password for every demo account: {DEMO_PASSWORD}")
        self.stdout.write("Admins:   " + ", ".join(user.username for user in admins))
        self.stdout.write("Teachers: " + ", ".join(user.username for user in teachers))
        self.stdout.write("Students: " + ", ".join(user.username for user in students))
        self.stdout.write("Parents:  " + ", ".join(user.username for user in parents))
        self.stdout.write(f"Circles: {len(circles)} | Season Circles: {len(season_circles)}")
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
            ("abu_bakr", "حلقة أبي بكر الصديق", GenderChoices.MALE, GovernorateChoices.CAPITAL),
            ("omar", "حلقة عمر بن الخطاب", GenderChoices.MALE, GovernorateChoices.HAWALLI),
            ("othman", "حلقة عثمان بن عفان", GenderChoices.MALE, GovernorateChoices.FARWANIYA),
            ("aisha", "حلقة عائشة أم المؤمنين", GenderChoices.FEMALE, GovernorateChoices.MUBARAK_AL_KABEER),
            ("fatima", "حلقة فاطمة الزهراء", GenderChoices.FEMALE, GovernorateChoices.AHMADI),
        ]
        circles = []
        for index, (name, name_ar, gender, governorate) in enumerate(circle_data):
            circle, _created = Circle.objects.get_or_create(
                name=name,
                defaults={
                    "name_ar": name_ar,
                    "gender": gender,
                    "description": "حلقة مباركة مخصصة لحفظ السنة النبوية وتدريس أصول الحديث وتلاوة المتون الحديثية.",
                    "start_date": date.today() - timedelta(days=30),
                    "end_date": date.today() + timedelta(days=90),
                    "status": Circle.Status.OPEN,
                    "governorate": governorate,
                    "teacher": teachers[index],
                },
            )
            circle.name_ar = name_ar
            circle.gender = gender
            circle.description = "حلقة مباركة مخصصة لحفظ السنة النبوية وتدريس أصول الحديث وتلاوة المتون الحديثية."
            circle.start_date = date.today() - timedelta(days=30)
            circle.end_date = date.today() + timedelta(days=90)
            circle.status = Circle.Status.OPEN
            circle.governorate = governorate
            circle.teacher = teachers[index]
            circle.save()
            circles.append(circle)
        return circles

    def _create_season(self):
        start_date = date.today() - timedelta(days=21)
        end_date = date.today() + timedelta(days=90)
        season, _created = Season.objects.get_or_create(
            title="موسم ربيع 2026 التجريبي",
            defaults={
                "start_date": start_date,
                "end_date": end_date,
                "status": Season.Status.ACTIVE,
                "notes": "Demo season for testing decoupled architecture.",
            },
        )
        season.start_date = start_date
        season.end_date = end_date
        season.status = Season.Status.ACTIVE
        season.save()
        return season

    def _create_season_circles(self, season, circles):
        season_circles = []
        for circle in circles:
            sc, _created = SeasonCircle.objects.get_or_create(
                season=season,
                circle=circle,
                defaults={
                    "supervisor": circle.teacher,
                    "capacity": 25,
                },
            )
            sc.supervisor = circle.teacher
            sc.save()
            generate_sessions_for_cycle(sc)
            season_circles.append(sc)
        return season_circles

    def _create_enrollments(self, students, season, season_circles, approved_by):
        enrollments = []
        for student, season_circle in zip(students, season_circles):
            # Clean up old active enrollments
            Enrollment.objects.filter(
                student=student,
                status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
            ).exclude(season=season).update(
                status=Enrollment.Status.WITHDRAWN,
                withdrawn_by=approved_by,
                withdrawn_at=timezone.now(),
            )

            enrollment = Enrollment.objects.filter(student=student, season=season).first()
            if enrollment is None:
                # Temporarily open registration to allow enroll_student_in_season service validation
                prev_status = season.status
                season.status = Season.Status.REGISTRATION_OPEN
                season.save()

                enrollment = enrollment_service.enroll_student_in_season(
                    student=student,
                    season=season,
                    enrolled_by=approved_by,
                )

                # Restore original status
                season.status = prev_status
                season.save()

            # Assign Circle
            enrollment = enrollment_service.assign_circle_to_enrollment(
                enrollment=enrollment,
                season_circle=season_circle,
                assigned_by=approved_by,
            )

            # Approve Enrollment
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
                Session.objects.filter(cycle=enrollment.season_circle)
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
                        "marked_by": enrollment.season_circle.supervisor or marked_by,
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
