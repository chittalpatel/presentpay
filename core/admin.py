from django.contrib import admin

from core.models import Department, Employee, Attendance


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name")

    def company_name(self, obj):
        return obj.company.name


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "hourly_pay", "department", "company")

    def company(self, obj):
        return obj.department.company.name


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "start", "end")

    def name(self, obj):
        return obj.employee.full_name
