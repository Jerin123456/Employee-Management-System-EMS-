from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Attendance, Employee, Leave, Payroll


# Create your tests here.
class PayrollPageTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='payroll-admin',
            password='test-password',
            is_staff=True,
        )
        self.employee = Employee.objects.create(
            first_name='Ada',
            last_name='Lovelace',
            email='ada@example.com',
            department='Engineering',
            designation='Engineer',
            salary='5000.00',
            date_of_birth='1990-01-01',
            gender='Female',
        )
        self.client.force_login(self.staff_user)

    def test_staff_can_view_payroll_page(self):
        response = self.client.get(reverse('payroll'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payroll history')
        self.assertContains(response, 'Add payroll record')

    def test_employee_can_view_only_their_own_payroll(self):
        employee_user = User.objects.create_user(
            username='employee',
            password='test-password',
        )
        own_employee = Employee.objects.create(
            user=employee_user,
            first_name='Grace',
            last_name='Hopper',
            email='grace@example.com',
            department='Engineering',
            designation='Engineer',
            salary='6000.00',
            date_of_birth='1990-01-01',
            gender='Female',
        )
        other_employee = Employee.objects.create(
            first_name='Katherine',
            last_name='Johnson',
            email='katherine@example.com',
            department='Engineering',
            designation='Engineer',
            salary='7000.00',
            date_of_birth='1990-01-01',
            gender='Female',
        )
        Payroll.objects.create(
            employee=own_employee,
            pay_period=timezone.localdate().replace(day=1),
            gross_pay='6000.00',
        )
        Payroll.objects.create(
            employee=other_employee,
            pay_period=timezone.localdate().replace(day=1),
            gross_pay='7000.00',
        )
        self.client.force_login(employee_user)

        response = self.client.get(reverse('payroll'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Grace Hopper')
        self.assertNotContains(response, 'Katherine Johnson')
        self.assertNotContains(response, 'Add payroll record')
        self.assertNotContains(response, 'Mark paid')
        self.assertContains(response, f'href="{reverse("payroll")}"')

    def test_employee_cannot_change_payroll_records(self):
        employee_user = User.objects.create_user(
            username='employee',
            password='test-password',
        )
        own_employee = Employee.objects.create(
            user=employee_user,
            first_name='Grace',
            last_name='Hopper',
            email='grace@example.com',
            department='Engineering',
            designation='Engineer',
            salary='6000.00',
            date_of_birth='1990-01-01',
            gender='Female',
        )
        record = Payroll.objects.create(
            employee=own_employee,
            pay_period=timezone.localdate().replace(day=1),
            gross_pay='6000.00',
        )
        self.client.force_login(employee_user)

        response = self.client.post(
            reverse('payroll'),
            {'action': 'mark_paid', 'payroll_id': record.pk},
        )

        record.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(record.status, Payroll.Status.UNPAID)

    def test_anonymous_user_is_sent_to_employee_sign_in(self):
        self.client.logout()

        response = self.client.get(reverse('payroll'))

        self.assertRedirects(
            response,
            f"{reverse('employee_login')}?next={reverse('payroll')}",
        )

    def test_staff_can_add_paid_payroll_record(self):
        response = self.client.post(
            reverse('payroll'),
            {
                'employee': self.employee.pk,
                'pay_period': '2026-11',
                'gross_pay': '5000.00',
                'deductions': '500.00',
                'status': Payroll.Status.PAID,
                'payment_date': '2026-11-30',
            },
        )

        self.assertRedirects(response, reverse('payroll'))
        record = Payroll.objects.get(employee=self.employee)
        self.assertEqual(record.pay_period.isoformat(), '2026-11-01')
        self.assertEqual(record.net_pay, 4500)

    def test_unpaid_record_can_be_marked_paid(self):
        record = Payroll.objects.create(
            employee=self.employee,
            pay_period='2026-11-01',
            gross_pay='5000.00',
            deductions='250.00',
        )

        response = self.client.post(
            reverse('payroll'),
            {'action': 'mark_paid', 'payroll_id': record.pk},
        )

        record.refresh_from_db()
        self.assertRedirects(response, reverse('payroll'))
        self.assertEqual(record.status, Payroll.Status.PAID)
        self.assertEqual(record.payment_date, timezone.localdate())

    def test_deductions_cannot_exceed_gross_pay(self):
        response = self.client.post(
            reverse('payroll'),
            {
                'employee': self.employee.pk,
                'pay_period': '2026-11',
                'gross_pay': '5000.00',
                'deductions': '5100.00',
                'status': Payroll.Status.UNPAID,
                'payment_date': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deductions cannot exceed gross pay.')
        self.assertFalse(Payroll.objects.exists())


class BackendNavigationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='employee@example.com',
            email='employee@example.com',
            password='test-password',
        )
        self.employee = Employee.objects.create(
            user=self.user,
            first_name='Ada',
            last_name='Lovelace',
            email='employee@example.com',
            department='Engineering',
            designation='Engineer',
            salary='5000.00',
            date_of_birth='1990-01-01',
            gender='Female',
        )

    def test_named_navigation_routes_resolve(self):
        route_names = (
            'homepage',
            'add_employee',
            'employee_login',
            'emphome',
            'attendance_history',
            'mark_attendance_page',
            'leave_request',
            'announcements',
            'payroll',
        )
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                self.assertTrue(reverse(route_name))

        self.assertTrue(reverse('mark_attendance', args=['Present']))

    def test_protected_pages_redirect_to_employee_sign_in(self):
        protected_pages = (
            'emphome',
            'attendance_history',
            'mark_attendance_page',
            'leave_request',
            'payroll',
        )
        for route_name in protected_pages:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertRedirects(
                    response,
                    f"{reverse('employee_login')}?next={reverse(route_name)}",
                )

    def test_login_returns_user_to_requested_page(self):
        destination = reverse('leave_request')

        response = self.client.post(
            f"{reverse('employee_login')}?next={destination}",
            {
                'email': self.user.email,
                'password': 'test-password',
                'next': destination,
            },
        )

        self.assertRedirects(response, destination)

    def test_login_rejects_external_next_destination(self):
        response = self.client.post(
            reverse('employee_login'),
            {
                'email': self.user.email,
                'password': 'test-password',
                'next': 'https://example.com/',
            },
        )

        self.assertRedirects(response, reverse('emphome'))

    def test_employee_pages_and_navigation_load(self):
        self.client.force_login(self.user)
        pages = (
            'homepage',
            'emphome',
            'attendance_history',
            'mark_attendance_page',
            'leave_request',
            'announcements',
            'payroll',
        )
        for route_name in pages:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, reverse('homepage'))
                self.assertContains(response, reverse('payroll'))

    def test_attendance_changes_require_post_and_valid_status(self):
        self.client.force_login(self.user)
        attendance_url = reverse('mark_attendance', args=['Present'])

        self.assertEqual(self.client.get(attendance_url).status_code, 405)

        response = self.client.post(attendance_url)

        self.assertRedirects(response, reverse('emphome'))
        self.assertTrue(
            Attendance.objects.filter(
                employee=self.user,
                date=timezone.localdate(),
                status='Present',
            ).exists()
        )

        invalid_response = self.client.post(
            reverse('mark_attendance', args=['Unknown'])
        )
        self.assertEqual(invalid_response.status_code, 404)

    def test_leave_requests_are_saved_for_the_signed_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('leave_request'),
            {
                'from_date': '2026-11-10',
                'to_date': '2026-11-12',
                'reason': 'Personal leave',
            },
        )

        self.assertRedirects(response, reverse('leave_request'))
        self.assertTrue(
            Leave.objects.filter(employee=self.user, reason='Personal leave').exists()
        )
