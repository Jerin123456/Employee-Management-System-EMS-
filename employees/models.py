from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank = True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=50)
    def __str__(self):
         return f"{self.first_name}{self.last_name}"



class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.status}"

class Leave(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.employee.username} - {self.status}"
class Announcement(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Payroll(models.Model):
    class Status(models.TextChoices):
        PAID = 'Paid', 'Paid'
        UNPAID = 'Unpaid', 'Unpaid'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
    pay_period = models.DateField()
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)

    class Meta:
        ordering = ['-pay_period', 'employee__first_name', 'employee__last_name']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'pay_period'],
                name='unique_payroll_employee_period',
            ),
        ]

    @property
    def net_pay(self):
        return self.gross_pay - self.deductions

    def clean(self):
        errors = {}
        if self.gross_pay is not None and self.gross_pay <= 0:
            errors['gross_pay'] = 'Gross pay must be greater than zero.'
        if (
            self.gross_pay is not None
            and self.deductions is not None
            and self.deductions > self.gross_pay
        ):
            errors['deductions'] = 'Deductions cannot exceed gross pay.'
        if self.status == self.Status.PAID and not self.payment_date:
            errors['payment_date'] = 'A payment date is required for paid payroll.'
        if self.status == self.Status.UNPAID and self.payment_date:
            errors['payment_date'] = 'Unpaid payroll cannot have a payment date.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.employee} - {self.pay_period:%B %Y}'
