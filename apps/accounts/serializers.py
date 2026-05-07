from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, ParentProfile
from .services import registration_service


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "role",
            "registration_status",
            "gender",
            "governorate",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "registration_status", "date_joined"]


class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "governorate",
            "password",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False, "allow_blank": True},
            "phone_number": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        if not registration_service.has_contact_method(attrs):
            raise serializers.ValidationError("Register with either an email address or a phone number.")
        return attrs

    def create(self, validated_data):
        return registration_service.create_pending_student(validated_data)


class ParentProfileSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    parent_full_name = serializers.CharField(source='parent.full_name', read_only=True)

    class Meta:
        model = ParentProfile
        fields = [
            "id",
            "parent",
            "parent_full_name",
            "student",
            "student_full_name",
            "status",
            "requested_at",
            "approved_at",
            "notes",
        ]
        read_only_fields = ["id", "parent", "status", "requested_at", "approved_at"]


class ParentProfileRequestSerializer(serializers.Serializer):
    student_username = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_student_username(self, value):
        try:
            student = User.objects.get(username=value, role=User.Roles.STUDENT)
        except User.DoesNotExist:
            raise serializers.ValidationError("Student not found.")
        return student

    def create(self, validated_data):
        parent = self.context['request'].user
        student = validated_data['student_username']
        notes = validated_data.get('notes', '')

        # Check if already linked
        if ParentProfile.objects.filter(parent=parent, student=student).exists():
            raise serializers.ValidationError("A link request already exists for this student.")

        return ParentProfile.objects.create(
            parent=parent,
            student=student,
            notes=notes
        )
