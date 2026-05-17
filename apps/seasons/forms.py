from django import forms
from .models import Season, SeasonCircle
from apps.accounts.models import User

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = [
            "title",
            "start_date",
            "end_date",
            "status",
            "default_session_start_time",
            "default_session_end_time",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثال: موسم صيف 2026"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "default_session_start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "default_session_end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "ملاحظات إضافية حول الموسم..."}),
        }


class SeasonCircleForm(forms.ModelForm):
    class Meta:
        model = SeasonCircle
        fields = ["circle", "supervisor", "capacity"]
        widgets = {
            "circle": forms.Select(attrs={"class": "form-select"}),
            "supervisor": forms.Select(attrs={"class": "form-select"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter supervisor dropdown to show only teachers and admins
        self.fields['supervisor'].queryset = User.objects.filter(
            role__in=[User.Roles.TEACHER, User.Roles.ADMIN],
            is_active=True
        )
