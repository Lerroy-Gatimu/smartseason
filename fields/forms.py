"""
fields/forms.py
---------------
Forms for creating/editing fields and logging field updates.
"""
from django import forms
from .models import Field, FieldUpdate
from accounts.models import User


class FieldForm(forms.ModelForm):
    """
    Admin form to create or edit a field.
    """
    class Meta:
        model = Field
        fields = [
            'name', 'crop_type', 'location',
            'planting_date', 'expected_harvest_date',
            'current_stage', 'assigned_to', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. North Block A',
            }),
            'crop_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Maize, Tomatoes, Beans',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Kiambu, Nakuru County (optional)',
            }),
            'planting_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'expected_harvest_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'current_stage': forms.Select(attrs={'class': 'form-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Admin notes (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show field agents in the assigned_to dropdown
        self.fields['assigned_to'].queryset = (
            User.objects.filter(role=User.Role.FIELD_AGENT, is_active=True)
            .order_by('first_name', 'username')
        )
        self.fields['assigned_to'].empty_label = '— Unassigned —'
        self.fields['expected_harvest_date'].required = False


class FieldUpdateForm(forms.ModelForm):
    """
    Form for field agents to log an update on a field.
    Agents can change the stage and add observations/notes.
    """
    class Meta:
        model = FieldUpdate
        fields = ['stage_at_update', 'notes']
        widgets = {
            'stage_at_update': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe what you observed: crop health, weather, pests, measurements…',
            }),
        }
        labels = {
            'stage_at_update': 'Current Stage',
            'notes': 'Observations / Notes',
        }
