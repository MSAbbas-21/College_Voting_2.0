from django import forms
from django.core.exceptions import ValidationError
from .models import Candidate
from elections.models import Election


class CandidateForm(forms.ModelForm):
    """Form for administrators to register and manage candidates."""
    class Meta:
        model = Candidate
        fields = ['election', 'name', 'student_id', 'department', 'position', 'manifesto', 'photo']
        widgets = {
            'election': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jordan Hayes'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS2022019'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'manifesto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Candidate goals, policy platform, and student advocacy commitments...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order elections by latest first
        self.fields['election'].queryset = Election.objects.all().order_by('-start_date')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check maximum file size (5MB limit)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Profile image size cannot exceed 5 MB.")
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
            ext = photo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported image format. Allowed: {', '.join(valid_extensions)}")
        return photo
