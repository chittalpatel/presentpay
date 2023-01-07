import datetime

from django import forms
from django.core.exceptions import ValidationError

from core.models import Department, Employee, Attendance


class EmployeeForm(forms.ModelForm):
    date_of_birth = forms.CharField(widget=forms.TextInput(attrs={"type": "date"}))
    joined_date = forms.CharField(widget=forms.TextInput(attrs={"type": "date"}))

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "date_of_birth",
            "address_line1",
            "address_line2",
            "address_line3",
            "city",
            "state",
            "country",
            "department",
            "role",
            "joined_date",
            "hourly_pay",
            "daily_break_hours",
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        self.fields["department"] = forms.ModelChoiceField(
            queryset=Department.objects.filter(company=user.company)
        )
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-user"


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


class BillingFilterForm(forms.Form):
    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]
    month = forms.ChoiceField(
        choices=MONTH_CHOICES, required=True, initial=datetime.date.today().month
    )
    year = forms.IntegerField(
        min_value=2020,
        max_value=datetime.date.today().year,
        required=True,
        initial=datetime.date.today().year,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-user"
