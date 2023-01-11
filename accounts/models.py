import enum

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class Company(models.Model):
    name = models.CharField(max_length=30, unique=True)
    phone = PhoneNumberField(blank=False, null=False)
    email = models.EmailField(null=False, blank=False)
    address_line1 = models.CharField(max_length=255, blank=False, null=False)
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    address_line3 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255, blank=False, null=False)
    state = models.CharField(max_length=2, blank=False, null=False)
    country = models.CharField(max_length=2, blank=False, null=False)

    # settings
    shift_start_time = models.TimeField(blank=True, null=True)
    ceiling_minutes = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        default=0,
        validators=[MaxValueValidator(59), MinValueValidator(0)],
    )


class User(AbstractUser):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="company_users",
    )
