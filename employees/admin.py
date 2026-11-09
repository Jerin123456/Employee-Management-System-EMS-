from django.contrib import admin
from .models import Employee
from .models import Attendance, Leave, Announcement, Payroll

# Register your models here.
admin.site.register(Employee)




@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'date', 'status')
    list_filter = ('status', 'date')

    def employee_name(self, obj):
        employee = Employee.objects.filter(email=obj.employee.email).first()

        if employee:
            return f"{employee.first_name} {employee.last_name}"

        return obj.employee.username

    employee_name.admin_order_field = 'employee'
    employee_name.short_description = 'EMPLOYEE'
@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'from_date',
        'to_date',
        'reason',
        'status'
    )

    list_filter = ('status', 'from_date')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'message')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'pay_period', 'gross_pay', 'deductions', 'net_pay', 'status', 'payment_date')
    list_filter = ('status', 'pay_period')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email')