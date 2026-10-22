from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = get_user_model()


class StudentRegistrationAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.edu',
            password='AdminPassword123'
        )

    def test_student_registration_success(self):
        """Test successful registration with auto pending status."""
        data = {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test.student@test.edu',
            'student_id': 'TEST202601',
            'department': 'CSE',
            'year_of_study': '2',
            'phone_number': '1234567890',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(student_id='TEST202601').exists())
        user = User.objects.get(student_id='TEST202601')
        self.assertEqual(user.approval_status, 'pending')
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_duplicate_student_id_rejected(self):
        """Test that registering with duplicate student_id is blocked."""
        User.objects.create_user(
            username='DUP001',
            student_id='DUP001',
            email='first@test.edu',
            password='Password123!'
        )
        data = {
            'first_name': 'Second',
            'last_name': 'Student',
            'email': 'second@test.edu',
            'student_id': 'DUP001',
            'department': 'CSE',
            'year_of_study': '1',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'student_id', 'This Student ID / Roll number is already registered.')

    def test_duplicate_email_rejected(self):
        """Test that registering with duplicate email is blocked."""
        User.objects.create_user(
            username='ROLL01',
            student_id='ROLL01',
            email='common@test.edu',
            password='Password123!'
        )
        data = {
            'first_name': 'Another',
            'last_name': 'Student',
            'email': 'common@test.edu',
            'student_id': 'ROLL02',
            'department': 'CSE',
            'year_of_study': '1',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'A user with this college email already exists.')

    def test_login_with_student_id_and_email(self):
        """Test login works using either student_id or college email."""
        student = User.objects.create_user(
            username='LOGIN01',
            student_id='LOGIN01',
            email='login.student@test.edu',
            password='SecretPassword123'
        )

        # 1. Login with student ID
        res1 = self.client.post(reverse('accounts:login'), {
            'credential': 'LOGIN01',
            'password': 'SecretPassword123',
        })
        self.assertEqual(res1.status_code, 302)
        self.client.logout()

        # 2. Login with email
        res2 = self.client.post(reverse('accounts:login'), {
            'credential': 'login.student@test.edu',
            'password': 'SecretPassword123',
        })
        self.assertEqual(res2.status_code, 302)

    def test_student_approval_and_rejection_by_admin(self):
        """Test admin can approve or reject a pending student."""
        student = User.objects.create_user(
            username='PEND01',
            student_id='PEND01',
            email='pend@test.edu',
            password='Password123',
            role='student',
            approval_status='pending'
        )
        self.assertFalse(student.is_approved_voter)

        # Admin logs in
        self.client.login(username='testadmin', password='AdminPassword123')

        # Approve student
        app_res = self.client.post(reverse('dashboard:student_approve', kwargs={'user_id': student.id}))
        self.assertEqual(app_res.status_code, 302)
        student.refresh_from_db()
        self.assertEqual(student.approval_status, 'approved')
        self.assertTrue(student.is_approved_voter)

        # Reject student
        rej_res = self.client.post(
            reverse('dashboard:student_reject', kwargs={'user_id': student.id}),
            {'rejection_reason': 'Invalid roll'}
        )
        self.assertEqual(rej_res.status_code, 302)
        student.refresh_from_db()
        self.assertEqual(student.approval_status, 'rejected')
        self.assertFalse(student.is_approved_voter)

    def test_non_admin_cannot_access_admin_dashboard(self):
        """Test regular student is blocked from administrative console."""
        student = User.objects.create_user(
            username='STU001',
            student_id='STU001',
            email='stu001@test.edu',
            password='Password123',
            role='student',
            approval_status='approved'
        )
        self.client.login(username='STU001', password='Password123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:student_dashboard'))
