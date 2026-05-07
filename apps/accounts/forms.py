from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.core.choices import GenderChoices, GovernorateChoices

from .models import User
from .services import registration_service


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False, max_length=20)
    gender = forms.ChoiceField(choices=GenderChoices.choices)
    governorate = forms.ChoiceField(choices=GovernorateChoices.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "governorate",
        )

    def clean(self):
        cleaned_data = super().clean()
        if not registration_service.has_contact_method(cleaned_data):
            raise forms.ValidationError("Register with either an email address or a phone number.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        registration_service.prepare_pending_student(user)
        if commit:
            user.save()
        return user
