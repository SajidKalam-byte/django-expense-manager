from django import forms
from .models import ProjectMeta

class ProjectMetaForm(forms.ModelForm):
    class Meta:
        model = ProjectMeta
        fields = ['total_budget', 'start_date', 'target_end_date']
        widgets = {
            'total_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
