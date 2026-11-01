import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from gym.models import Plan, Member, Equipment, Enquiry, Trainer


class GymManagementSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            password='Password123!',
            email='staff@example.com',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='Password123!',
            email='regular@example.com',
            is_staff=False
        )
        self.test_plan = Plan.objects.create(name='Gold Plan', amount=1500.00, duration=90)

    def test_unauthenticated_redirections(self):
        """Unauthenticated requests to staff management views must redirect to login."""
        protected_urls = [
            reverse('home'),
            reverse('view_member'),
            reverse('view_plan'),
            reverse('view_equipment'),
            reverse('view_enquiry'),
            reverse('view_trainer'),
            reverse('export_member_csv'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, f"Expected 302 redirect for {url}")
            self.assertIn(reverse('login'), response.url)

    def test_admin_login_view_with_standard_and_legacy_fields(self):
        """admin_login_view should authenticate with username/password or uname/pwd."""
        # Test standard fields (username / password)
        resp1 = self.client.post(reverse('admin_login'), {
            'username': 'staffadmin',
            'password': 'Password123!'
        })
        self.assertEqual(resp1.status_code, 302)
        self.assertIn(reverse('home'), resp1.url)

        # Test legacy fields (uname / pwd)
        self.client.logout()
        resp2 = self.client.post(reverse('admin_login'), {
            'uname': 'staffadmin',
            'pwd': 'Password123!'
        })
        self.assertEqual(resp2.status_code, 302)
        self.assertIn(reverse('home'), resp2.url)

    def test_add_member_with_selected_plan(self):
        """Add_Member should link to the selected Plan instance instead of creating dummy plans."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('add_member'), {
            'name': 'John Doe',
            'contact': '9876543210',
            'emailid': 'johndoe@example.com',
            'dob': '1995-05-15',
            'gender': 'Male',
            'membership_type': 'vip',
            'plan': str(self.test_plan.id),
            'address': '123 Main Street',
            'emergency_contact': '9876543211',
            'medical_conditions': 'None',
            'joindate': '2026-01-01',
            'expdate': '2026-04-01',
            'initialamount': '1500.00'
        })
        self.assertEqual(response.status_code, 200)
        member = Member.objects.filter(emailid='johndoe@example.com').first()
        self.assertIsNotNone(member)
        self.assertEqual(member.plan.id, self.test_plan.id)
        self.assertEqual(member.plan.name, 'Gold Plan')

    def test_add_plan_duration_handling(self):
        """Add_Plan should safely parse duration numbers."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('add_plan'), {
            'name': 'Platinum Plan',
            'amount': '3000',
            'duration': '180'
        })
        self.assertEqual(response.status_code, 200)
        plan = Plan.objects.filter(name='Platinum Plan').first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.duration, 180)

    def test_delete_non_existent_item_returns_404(self):
        """Deleting a non-existent item should return 404 instead of throwing unhandled 500 error."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.get(reverse('delete_member', kwargs={'pid': 999999}))
        self.assertEqual(response.status_code, 404)

    def test_forgot_password_view_post(self):
        """forgot_password view should accept POST with email and render template."""
        response = self.client.post(reverse('forgot_password'), {
            'email': 'staff@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password reset link sent")
