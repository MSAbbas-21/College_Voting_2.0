from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom user model for College Voting Management System.
    Supports Students and Administrators with approval workflow.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Administrator'),
    )

    APPROVAL_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    YEAR_CHOICES = (
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('PG', 'Post-Graduate'),
    )

    DEPARTMENT_CHOICES = (
        ('CSE', 'Computer Science & Engineering'),
        ('IT', 'Information Technology'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EE', 'Electrical Engineering'),
        ('MBA', 'Management Studies / MBA'),
        ('BSC', 'Applied Sciences'),
    )

    # Core identification fields
    email = models.EmailField(
        unique=True,
        verbose_name="College Email Address",
        help_text="Official college email address."
    )
    student_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Student ID / Roll Number",
        help_text="Official college issued roll number or student ID."
    )
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        default='CSE',
        verbose_name="Department"
    )
    year_of_study = models.CharField(
        max_length=10,
        choices=YEAR_CHOICES,
        default='1',
        verbose_name="Year of Study"
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="User Role"
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='pending',
        verbose_name="Approval Status"
    )
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_students',
        verbose_name="Approved By Admin"
    )
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approval Date"
    )
    rejection_reason = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Rejection / Note"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone Number"
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name="Profile Photo"
    )

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        name = self.get_full_name() or self.username
        if self.student_id:
            return f"{name} ({self.student_id})"
        return f"{name} ({self.role})"

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_approved_voter(self):
        """Returns True if the student account is verified and active."""
        return self.is_student and self.approval_status == 'approved' and self.is_active

    def approve(self, admin_user):
        """Approve a student account for voting."""
        self.approval_status = 'approved'
        self.approved_by = admin_user
        self.approval_date = timezone.now()
        self.rejection_reason = ''
        self.save(update_fields=['approval_status', 'approved_by', 'approval_date', 'rejection_reason'])

    def reject(self, admin_user, reason=""):
        """Reject a student account registration."""
        self.approval_status = 'rejected'
        self.approved_by = admin_user
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=['approval_status', 'approved_by', 'approval_date', 'rejection_reason'])

    def save(self, *args, **kwargs):
        # Superusers and staff default to admin role and approved status
        if self.is_superuser or self.is_staff:
            self.role = 'admin'
            self.approval_status = 'approved'
        super().save(*args, **kwargs)
