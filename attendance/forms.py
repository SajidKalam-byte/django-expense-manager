from django import forms
from .models import Attendance, WorkType

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'date',
            'workers_count',
            'work_type',
            'custom_work_note',
            'wage_per_worker',
            'is_half_day',
            'phase',
            'wallet'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'workers_count': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_workers_count'}),
            'work_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_work_type'}),
            'custom_work_note': forms.TextInput(attrs={'class': 'form-control'}),
            'wage_per_worker': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_wage_per_worker', 'step': '0.01'}),
            'is_half_day': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_half_day'}),
            'phase': forms.TextInput(attrs={'class': 'form-control'}),
            'wallet': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        work_type = cleaned_data.get('work_type')
        wage_per_worker = cleaned_data.get('wage_per_worker')
        
        # Enforce consistency:
        if work_type:
            cleaned_data['wage_per_worker'] = work_type.default_wage
        elif not wage_per_worker:
            raise forms.ValidationError("You must provide either a predefined Work Type or a Manual Wage.")
            
        return cleaned_data


class WorkTypeForm(forms.ModelForm):
    class Meta:
        model = WorkType
        fields = ['name', 'default_wage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_wage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
