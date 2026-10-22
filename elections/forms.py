from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Election


class ElectionForm(forms.ModelForm):
    """Form to create and update elections."""
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label="Voting Start Time"
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label="Voting End Time"
    )

    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'status', 'is_published', 'banner_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Student Council Presidential Election 2026'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Guidelines, eligibility, and rules for voting...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end:
            if end <= start:
                raise ValidationError("Election end time must be later than the start time.")

        return cleaned_data
