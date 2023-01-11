import datetime

import dateutil.parser
import pytz
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.db.models import Q

from core.forms import EmployeeForm, BillingFilterForm
from core.models import Employee, Attendance
from core.utils import str_to_time, str_to_date, get_time_diff, seconds_to_hours_minutes


def test(request):
    return render(request, "attendance/create.html")


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


@login_required
def employee_list(request):
    employees = (
        Employee.objects.filter(
            department__company=request.user.company, is_active=True
        )
        .order_by("-id")
        .all()
    )
    return render(request, "employee/list.html", {"employees": employees})


def get_employee_by_pk(pk, user):
    employee = Employee.objects.filter(pk=pk, is_active=True).first()
    if employee and employee.department.company == user.company:
        return employee
    raise PermissionDenied


@login_required
def employee_detail(request, pk):
    employee = get_employee_by_pk(pk=pk, user=request.user)
    return render(request, "employee/detail.html", {"employee": employee})


class CreateEmployeeView(CreateView):
    model = Employee
    template_name = "employee/create.html"
    form_class = EmployeeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        emp_id = self.kwargs["pk"]
        return reverse_lazy("employee_detail", kwargs={"pk": emp_id})


class UpdateEmployeeView(UpdateView):
    model = Employee
    template_name = "employee/update.html"
    form_class = EmployeeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        emp_id = self.kwargs["pk"]
        return reverse_lazy("employee_detail", kwargs={"pk": emp_id})


def is_duplicate_attendance(date, start, end, exclude=None):
    if end:
        return (
            Attendance.objects.filter(
                (Q(start__lte=start) & Q(end__gt=start))
                | (Q(start__lt=end) & Q(end__gte=end))
                | (Q(start__gte=start) & Q(end__lte=end)),
                date=date,
                is_deleted=False,
            )
            .exclude(pk=exclude)
            .exists()
        )
    return Attendance.objects.filter(
        Q(start__lte=start) & Q(end__gt=start),
        date=date,
    ).exists()


@login_required
def attendance(request):
    if request.method == "GET":
        india_tz = pytz.timezone("Asia/Kolkata")
        total_days_till_today = 3
        today = datetime.datetime.now(india_tz).date()
        employees = Employee.objects.filter(
            is_active=True,
            department__company=request.user.company,
        ).all()
        attendances = (
            Attendance.objects.filter(
                date__lte=today,
                date__gte=today - datetime.timedelta(days=total_days_till_today - 1),
                employee__in=employees,
                is_deleted=False,
            )
            .order_by("date", "start")
            .all()
        )
        dates = [
            today - datetime.timedelta(days=days)
            for days in reversed(range(total_days_till_today))
        ]
        data = {}
        for emp in employees:
            data[emp] = {date: [] for date in dates}
        for attn in attendances:
            if attn.date in data[attn.employee]:
                data[attn.employee][attn.date].append(attn)

        return render(request, "attendance/create.html", {"dates": dates, "data": data})

    elif request.method == "POST":
        employee = get_employee_by_pk(pk=request.POST["employee_id"], user=request.user)
        date = str_to_date(request.POST["date"])
        start = str_to_time(request.POST["start"])
        end = str_to_time(request.POST["end"])
        created = False
        if not is_duplicate_attendance(date, start, end):
            Attendance.objects.create(
                employee=employee,
                date=date,
                start=start,
                end=end,
                hourly_pay=int(request.POST["pay"]),
                daily_break_minutes=int(request.POST["break"]),
            )
            created = True
        return get_attendance_by_employee(
            employee=employee,
            date=date,
            message=None
            if created
            else "Attendance is overlapping with existing attendance",
        )


def get_attendance_by_employee(employee, date, message=None):
    attendances = (
        Attendance.objects.filter(date=date, employee=employee, is_deleted=False)
        .order_by("start")
        .all()
    )
    response = {
        "data": [
            {
                "id": attn.id,
                "start": attn.start,
                "end": attn.end,
                "is_valid": attn.is_valid,
                "pay": attn.hourly_pay,
                "break": attn.break_minutes,
            }
            for attn in attendances
        ],
        "message": message,
    }
    return JsonResponse(response)


def get_attendance_or_404(attn_id):
    attn = get_object_or_404(Attendance, pk=attn_id)
    if attn.is_deleted:
        raise Http404("Attendance record not found.")
    return attn


@login_required
def update_attendance(request, attn_id):
    if request.method == "POST":
        attn = get_attendance_or_404(attn_id)
        emp = get_employee_by_pk(attn.employee_id, request.user)
        start = str_to_time(request.POST["start"])
        end = str_to_time(request.POST["end"])
        updated = False
        if not is_duplicate_attendance(attn.date, start, end, exclude=attn.id):
            attn.start = start
            attn.end = end
            attn.hourly_pay = int(request.POST["pay"])
            attn.break_minutes = int(request.POST["break"])
            attn.save()
            updated = True
        return get_attendance_by_employee(
            employee=emp,
            date=attn.date,
            message=None
            if updated
            else "Attendance is overlapping with existing attendance",
        )


@login_required
def delete_attendance(request, attn_id):
    if request.method == "POST":
        attn = get_attendance_or_404(attn_id)
        emp = get_employee_by_pk(attn.employee_id, request.user)
        attn.is_deleted = True
        attn.save()
        return get_attendance_by_employee(employee=emp, date=attn.date)


@login_required
def list_employee_attendances(request, pk):
    emp = get_employee_by_pk(pk=pk, user=request.user)

    date_range = request.GET.get("fromtodate")
    if date_range:
        start, end = date_range.split(",")
        start = dateutil.parser.parse(start).date()
        end = dateutil.parser.parse(end).date()
    else:
        india_tz = pytz.timezone("Asia/Kolkata")
        start = datetime.datetime.now(india_tz).date()
        end = start

    date_map = {
        (end - datetime.timedelta(days=x)): [] for x in range((end - start).days + 1)
    }
    attns = (
        Attendance.objects.filter(
            employee=emp, date__gte=start, date__lte=end, is_deleted=False
        )
        .order_by("date", "start")
        .all()
    )
    for attn in attns:
        if attn.date in date_map:
            date_map[attn.date].append(attn)
    return render(
        request,
        "attendance/employee_attendance.html",
        {"data": date_map, "employee": emp, "start": start, "end": end},
    )


@login_required
def view_employee_billing(request, pk):
    emp = get_employee_by_pk(pk=pk, user=request.user)
    month = request.GET.get("month")
    year = request.GET.get("year")
    if not (month and year):
        month = datetime.date.today().month
        year = datetime.date.today().year

    attns = Attendance.objects.filter(
        employee=emp,
        date__year=year,
        date__month=month,
        is_deleted=False,
    ).all()

    data = {
        "cost": 0,
        "work": (0, 0),
    }
    ceiling_minutes = request.user.company.ceiling_minutes
    for attn in attns:
        if not attn.is_valid:
            continue

        work_seconds = get_time_diff(start=attn.start, end=attn.end)
        break_seconds = attn.break_minutes * 60
        effective_seconds = max(work_seconds - break_seconds, 0)
        hours, minutes = seconds_to_hours_minutes(effective_seconds)
        if (minutes + ceiling_minutes) >= 60:
            hours += 1
            minutes = 0
        hours_in_decimal = hours + (minutes / 60)
        cost = hours_in_decimal * attn.hourly_pay

        data["work"] = (data["work"][0] + hours, data["work"][1] + minutes)
        data["cost"] += cost

    data["cost"] = round(data["cost"])
    data["work"] = (data["work"][0] + (data["work"][1] // 60), data["work"][1] % 60)
    data["work"] = f"{data['work'][0]} hours and {data['work'][1]} minutes"

    return render(
        request,
        "billing/employee_billing.html",
        {
            "data": data,
            "employee": emp,
            "form": BillingFilterForm(initial={"month": int(month), "year": int(year)}),
        },
    )
