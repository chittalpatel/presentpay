# Generated by Django 4.1.3 on 2023-01-11 12:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_company_shift_start_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="ceiling_minutes",
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[
                    django.core.validators.MaxValueValidator(59),
                    django.core.validators.MinValueValidator(0),
                ],
            ),
        ),
    ]