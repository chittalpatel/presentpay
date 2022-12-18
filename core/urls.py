from django.contrib.auth.decorators import login_required
from django.urls import path

from core import views

urlpatterns = [
    path("test/", views.test, name="test"),
    path("", views.dashboard, name="dashboard"),
    path("employees/list/", views.employee_list, name="employee_list"),
    path("employees/detail/<int:pk>/", views.employee_detail, name="employee_detail"),
    path(
        "employees/create/",
        login_required(views.CreateEmployeeView.as_view()),
        name="employee_create",
    ),
    path(
        "employees/update/<int:pk>/",
        login_required(views.UpdateEmployeeView.as_view()),
        name="employee_update",
    ),
    path("attendance/", views.attendance, name="attendance"),
    path(
        "attendance/<int:attn_id>/update/",
        views.update_attendance,
        name="update_attendance",
    ),
    path(
        "attendance/<int:attn_id>/delete/",
        views.delete_attendance,
        name="delete_attendance",
    ),
]
