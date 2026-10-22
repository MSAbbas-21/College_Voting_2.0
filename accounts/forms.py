from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser


class StudentRegistrationForm(forms.ModelForm):
    """
    Registration form for college students with validation for uniqueness,
    password strength, and auto-assignment to 'pending' status.
    """
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Alex'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Morgan'})
    )
    email = forms.EmailField(
        required=True,
        label="College Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'alex.m@college.edu'})
    )
    student_id = forms.CharField(
        max_length=30,
        required=True,
        label="Student Roll / ID Number",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS2023048'})
    )
    department = forms.ChoiceField(
        choices=CustomUser.DEPARTMENT_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year_of_study = forms.ChoiceField(
        choices=CustomUser.YEAR_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Mobile Number (Optional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 019-2834'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Minimum 8 characters'}),
        help_text="Must be at least 8 characters long with letters and numbers."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'student_id', 'department', 'year_of_study', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this college email already exists.")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id', '').strip().upper()
        if CustomUser.objects.filter(student_id__iexact=student_id).exists():
            raise ValidationError("This Student ID / Roll number is already registered.")
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd_confirm = cleaned_data.get('confirm_password')

        if pwd and pwd_confirm:
            if pwd != pwd_confirm:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                # Validate password with Django validators
                try:
                    validate_password(pwd)
                except ValidationError as e:
                    self.add_error('password', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use student_id as the unique username
        user.username = self.cleaned_data['student_id']
        user.set_password(self.cleaned_data['password'])
        user.role = 'student'
        user.approval_status = 'pending'
        user.is_active = True
        if commit:
            user.save()
        return user


class StudentLoginForm(forms.Form):
    """
    Login form allowing students or admins to log in with either
    Student ID, Email, or Username.
    """
    credential = forms.CharField(
        label="Student ID or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Student ID or College Email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        credential = cleaned_data.get('credential', '').strip()
        password = cleaned_data.get('password', '')

        if credential and password:
            # Check if credential matches username, email, or student_id
            user = None
            if '@' in credential:
                user_match = CustomUser.objects.filter(email__iexact=credential).first()
                if user_match:
                    user = authenticate(username=user_match.username, password=password)
            else:
                user_match = CustomUser.objects.filter(student_id__iexact=credential).first()
                if user_match:
                    user = authenticate(username=user_match.username, password=password)
                else:
                    user = authenticate(username=credential, password=password)

            if user is None:
                raise ValidationError("Invalid Student ID/Email or password. Please verify your credentials.")
            elif not user.is_active:
                raise ValidationError("Your account has been deactivated. Please contact the college administrator.")

            self.user = user

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class StudentProfileUpdateForm(forms.ModelForm):
    """
    Student profile edit form (phone number, profile photo).
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
