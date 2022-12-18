import datetime
import random

from accounts.models import User, Company
from core.models import Employee, Department, Attendance
from faker import Faker
from django.core.management.base import BaseCommand

fake = Faker()
Faker.seed(0)


def create_company():
    company = Company.objects.filter(name="My Company").first()
    if company:
        return company
    return Company.objects.create(
        name="My Company",
        phone=fake.phone_number(),
        email=fake.email(),
        address_line1=fake.address(),
        city="Vadodara",
        state="GJ",
        country="IN",
    )


def create_superuser(company):
    if User.objects.filter(username="test").exists():
        return
    User.objects.create_superuser(
        username="test",
        password="test",
        email="a@b.com",
        company=company,
    )


def create_departments():
    if Department.objects.exists():
        return
    for company in Company.objects.all():
        for _ in range(random.randint(2, 5)):
            Department.objects.create(name=fake.company(), company=company)


def create_employees():
    if Employee.objects.exists():
        return
    for dept in Department.objects.all():
        for _ in range(random.randint(5, 25)):
            profile = fake.profile()
            Employee.objects.create(
                first_name=profile.get("name", "").split(" ")[0],
                last_name=profile.get("name", "").split(" ")[1],
                phone=fake.phone_number(),
                email=profile.get("mail"),
                role=profile.get("job"),
                department=dept,
                joined_date=fake.date_between(start_date="-3y"),
                date_of_birth=profile.get("birthdate"),
                gender=profile.get("sex"),
                address_line1=profile.get("address"),
                city=random.choice(["Vadodara", "Surat", "Ahmedabad", "Rajkot"]),
                state="GJ",
                country="IN",
            )


def create_attendances():
    if Attendance.objects.exists():
        return
    for emp in Employee.objects.all():
        for history in range(3):
            if random.randint(1, 100) % 4 == 0:
                continue
            dt = datetime.date.today() - datetime.timedelta(days=history)
            Attendance.objects.create(
                employee=emp,
                date=dt,
                start=datetime.time(
                    hour=random.randint(6, 9), minute=random.randint(0, 59)
                ),
                end=datetime.time(
                    hour=random.randint(17, 22), minute=random.randint(0, 59)
                )
                if random.randint(1, 100) % 4
                else None,
                hourly_pay=random.randint(20, 60),
            )


def seed():
    create_superuser(create_company())
    create_departments()
    create_employees()
    create_attendances()


class Command(BaseCommand):
    help = "Seed database"

    def handle(self, *args, **kwargs):
        seed()
