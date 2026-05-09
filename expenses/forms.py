from decimal import Decimal, InvalidOperation
from django import forms
from django.forms import inlineformset_factory
from .models import Expense, Category, ExpensePayment, ExpenseItem

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'type', 'amount', 'category', 'subcategory', 'vendor', 'payment_mode', 'invoice_number', 'date', 'phase', 'notes', 'file']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional details about this expense...'}),
            'title': forms.TextInput(attrs={'placeholder': 'E.g., Cement Bags, Contractor Advance...'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'invoice_number': forms.TextInput(attrs={'placeholder': 'Invoice or Receipt No.'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }


class ExpensePaymentForm(forms.ModelForm):
    class Meta:
        model = ExpensePayment
        fields = ['wallet', 'amount']
        widgets = {
            'wallet': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class BaseExpensePaymentFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.expense_amount = kwargs.pop('expense_amount', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()


ExpensePaymentFormSet = inlineformset_factory(
    Expense,
    ExpensePayment,
    form=ExpensePaymentForm,
    formset=BaseExpensePaymentFormSet,
    extra=1,
    can_delete=True
)


class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['name', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class BaseExpenseItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.expense_amount = kwargs.pop('expense_amount', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()


ExpenseItemFormSet = inlineformset_factory(
    Expense,
    ExpenseItem,
    form=ExpenseItemForm,
    formset=BaseExpenseItemFormSet,
    extra=1,
    can_delete=True
)
