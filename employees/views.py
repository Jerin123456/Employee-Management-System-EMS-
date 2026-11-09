from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from decimal import Decimal
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Sum
from .models import Attendance, Announcement
from .models import Leave, Announcement, Payroll
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from employees.models import Employee
from django.contrib.auth.decorators import login_required
from .forms import PayrollForm




# Create your views here.
def add_employee(request):

    if request.method == "POST":

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        department = request.POST["department"]
        designation = request.POST["designation"]
        salary = request.POST["salary"]
        gender = request.POST.get("gender")
        date_of_birth = request.POST["date_of_birth"]

        password = request.POST["password"]

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        Employee.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            
            department=department,
            designation=designation,
            salary=salary,
            gender=gender,
            date_of_birth=date_of_birth
        )

        return redirect("homepage")

    return render(request, "add-employee.html")
def employee_login(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.user.is_authenticated:
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('emphome')

    if request.method == "POST":

        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("emphome")

        return render(request, "emplogin.html", {
            "error": "Invalid email or password",
            "next": next_url,
        })

    return render(request, "emplogin.html", {"next": next_url})


from django.db.models import Avg
from .models import Employee

def home(request):


    total_employees = Employee.objects.count()

    total_departments = Employee.objects.values(
        "department"
    ).distinct().count()

    average_salary = Employee.objects.aggregate(
        Avg("salary")
    )["salary__avg"]
    today = date.today()
    context = {
        "total_employees": total_employees,
        "total_departments": total_departments,
        'today': today,
    }



    return render(request, "homepage.html", context,)

@login_required(login_url='employee_login')
def emphome(request):
    return render(request, "emphome.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone

@login_required(login_url='employee_login')
@require_POST
def mark_attendance(request, status):
    if status not in dict(Attendance.STATUS_CHOICES):
        raise Http404("Unknown attendance status.")

    today = timezone.localdate()
    Attendance.objects.update_or_create(
        employee=request.user,
        date=today,
        defaults={'status': status},
    )
    return redirect('emphome')


@login_required(login_url='employee_login')
def mark_attendance_page(request):
    return render(request, 'mark attendance.html')







@login_required(login_url='employee_login')
def attendance_history(request):
    records = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')

    return render(
        request,
        'attendance history.html',
        {'records': records}
    )

@login_required(login_url='employee_login')
def leave_request(request):

    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        reason = request.POST.get("reason")

        Leave.objects.create(
            employee=request.user,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            status="Pending"
        )

        return redirect("leave_request")

    leaves = Leave.objects.filter(
        employee=request.user
    ).order_by("-from_date")

    return render(
        request,
        "request leave.html",
        {"leaves": leaves}
    )

def announcements(request):
    announcements = Announcement.objects.all().order_by("-created_at")

    return render(
        request,
        "announcements.html",
        {"announcements": announcements}
    )


@login_required(login_url='employee_login')
def payroll(request):
    can_manage_payroll = request.user.is_staff
    if can_manage_payroll:
        records = Payroll.objects.select_related('employee')
    else:
        employee = Employee.objects.filter(user=request.user).first()
        if employee is None:
            return HttpResponseForbidden(
                "Your account is not linked to an employee record."
            )
        if request.method == 'POST':
            return HttpResponseForbidden(
                "You do not have permission to change payroll records."
            )
        records = Payroll.objects.filter(employee=employee).select_related('employee')

    today = timezone.localdate()
    if request.method == 'POST':
        if request.POST.get('action') == 'mark_paid':
            record = get_object_or_404(
                Payroll,
                pk=request.POST.get('payroll_id'),
                status=Payroll.Status.UNPAID,
            )
            record.status = Payroll.Status.PAID
            record.payment_date = timezone.localdate()
            record.save(update_fields=['status', 'payment_date'])
            messages.success(request, f'{record.employee} was marked as paid.')
            return redirect('payroll')

        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll record added.')
            return redirect('payroll')
    else:
        form = PayrollForm(initial={'pay_period': today.replace(day=1)})

    this_month = today.replace(day=1)
    monthly_records = records.filter(
        pay_period__year=this_month.year,
        pay_period__month=this_month.month,
    )
    zero = Decimal('0.00')

    def net_total(queryset):
        gross = queryset.aggregate(total_gross=Sum('gross_pay'))['total_gross'] or zero
        deductions = queryset.aggregate(total_deductions=Sum('deductions'))['total_deductions'] or zero
        return gross - deductions

    context = {
        'form': form,
        'records': records,
        'can_manage_payroll': can_manage_payroll,
        'current_month': this_month,
        'monthly_net': net_total(monthly_records),
        'paid_net': net_total(monthly_records.filter(status=Payroll.Status.PAID)),
        'outstanding_net': net_total(monthly_records.filter(status=Payroll.Status.UNPAID)),
    }
    return render(request, 'payroll.html', context)
