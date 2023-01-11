# Generated by Django 4.1.3 on 2023-01-11 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_employee_shift_start_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="attendance",
            old_name="break_hours",
            new_name="break_minutes",
        ),
        migrations.RemoveField(
            model_name="employee",
            name="daily_break_hours",
        ),
        migrations.AddField(
            model_name="employee",
            name="daily_break_minutes",
            field=models.PositiveIntegerField(default=30),
        ),
    ]
