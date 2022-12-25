import datetime

import dateutil.parser
import pytz
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from core.forms import EmployeeForm
from core.models import Employee, Attendance
from core.utils import str_to_time, str_to_date


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
    return render(request, "employee/detail.html", {"obj": employee})


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
        Attendance.objects.create(
            employee=employee,
            date=date,
            start=str_to_time(request.POST["start"]),
            end=str_to_time(request.POST["end"]),
            hourly_pay=employee.hourly_pay,
        )
        return get_attendance_by_employee(employee=employee, date=date)


def get_attendance_by_employee(employee, date):
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
            }
            for attn in attendances
        ]
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
        attn.start = str_to_time(request.POST["start"])
        attn.end = str_to_time(request.POST["end"])
        attn.save()
        return get_attendance_by_employee(employee=emp, date=attn.date)


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
        (start + datetime.timedelta(days=x)): [] for x in range((end - start).days + 1)
    }
    attns = (
        Attendance.objects.filter(employee=emp, date__gte=start, date__lte=end)
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
