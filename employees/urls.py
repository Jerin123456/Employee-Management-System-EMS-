from django.urls import path
from . import  views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('employee_login/', views.employee_login, name='employee_login'),
    path("emphome/", views.emphome, name='emphome'),
path(
    'attendance/history/',
    views.attendance_history,
    name='attendance_history'
),

path(
    'markattendance/',
    views.mark_attendance_page,
    name='mark_attendance_page'
),

path(
    'attendance/<str:status>/',
    views.mark_attendance,
    name='mark_attendance'
),
path('leave-request/', views.leave_request, name='leave_request'),
path('announcements/', views.announcements, name='announcements'),
path('payroll/', views.payroll, name='payroll'),



]