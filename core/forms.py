from django import forms
from django.core.exceptions import ValidationError

from core.models import Department, Employee, Attendance


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["department"] = forms.ModelChoiceField(
            queryset=Department.objects.filter(company=user.company)
        )


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        if start and end and start > end:
            raise ValidationError("Start time cannot be greater than end time.")
