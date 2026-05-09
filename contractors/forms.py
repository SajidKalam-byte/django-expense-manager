from django import forms
from .models import Contractor, ContractorPayment


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['name', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContractorPaymentForm(forms.ModelForm):
    class Meta:
        model = ContractorPayment
        fields = ['contractor', 'date', 'amount', 'wallet', 'reason', 'phase']
        widgets = {
            'contractor': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'wallet': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'phase': forms.TextInput(attrs={'class': 'form-control'}),
        }
