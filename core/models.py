import datetime

from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from accounts.models import Company


class Department(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True, default="")

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Employee(models.Model):
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other"))

    first_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64, blank=True, default="")
    last_name = models.CharField(max_length=64, blank=True, default="")
    phone = PhoneNumberField(blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=128, blank=True, default="")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    joined_date = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    address_line1 = models.CharField(max_length=255, blank=False, null=False)
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    address_line3 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255, blank=False, null=False)
    state = models.CharField(max_length=2, blank=False, null=False)
    country = models.CharField(max_length=2, blank=False, null=False)
    hourly_pay = models.PositiveIntegerField(blank=False, null=False)
    daily_break_minutes = models.PositiveIntegerField(
        blank=False, null=False, default=30
    )
    is_active = models.BooleanField(blank=False, null=False, default=True)
    shift_start_time = models.TimeField(blank=True, null=True)

    @property
    def full_name(self):
        name = self.first_name
        if self.middle_name:
            name = f"{name} {self.middle_name}"
        if self.last_name:
            name = f"{name} {self.last_name}"
        return name

    @property
    def age(self):
        if self.date_of_birth:
            return datetime.datetime.today().year - self.date_of_birth.year

    def get_absolute_url(self):
        return reverse("employee_detail", args=[self.id])

    def __str__(self):
        return self.full_name


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, null=False, blank=False
    )

    date = models.DateField(blank=False, null=False)
    start = models.TimeField(blank=False, null=False)
    end = models.TimeField(blank=True, null=True)
    hourly_pay = models.PositiveIntegerField(blank=False, null=False)
    break_minutes = models.PositiveIntegerField(blank=False, null=False)
    is_deleted = models.BooleanField(default=False)

    @property
    def is_valid(self):
        return (
            True
            if self.date and self.start and self.end and self.start < self.end
            else False
        )
