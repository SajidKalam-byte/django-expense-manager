from decimal import Decimal, InvalidOperation
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm, ExpensePaymentFormSet, ExpenseItemFormSet
from wallets.services import (
    delete_expense_transaction,
    create_expense_transactions_for_expense,
    replace_expense_transactions_for_expense
)

class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        qs = Expense.objects.select_related('category', 'wallet', 'vendor').prefetch_related('items').order_by('-date', '-created_at')

        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')

        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)

        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)

        vendor = self.request.GET.get('vendor')
        if vendor:
            qs = qs.filter(vendor_id=vendor)

        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(vendor__name__icontains=query)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Category
        from vendors.models import Vendor
        from datetime import date, timedelta
        import calendar

        context['categories'] = Category.objects.all()
        context['vendors'] = Vendor.objects.all()
        
        today = date.today()
        context['today_str'] = today.isoformat()
        context['last_7_days_str'] = (today - timedelta(days=7)).isoformat()
        
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        context['this_month_start_str'] = first_day.isoformat()
        context['this_month_end_str'] = last_day.isoformat()
        
        from django.conf import settings
        context['LARGE_EXPENSE_THRESHOLD'] = getattr(settings, 'LARGE_EXPENSE_THRESHOLD', 50000)
        
        return context

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')

    def get_formset(self, data=None):
        amount = self._get_amount_from_request(data)
        return ExpensePaymentFormSet(
            data,
            instance=self.object or Expense(),
            prefix='payments',
            expense_amount=amount
        )

    def get_item_formset(self, data=None):
        amount = self._get_amount_from_request(data)
        return ExpenseItemFormSet(
            data,
            instance=self.object or Expense(),
            prefix='items',
            expense_amount=amount
        )

    def _get_amount_from_request(self, data):
        if not data:
            return None
        raw = data.get('amount')
        if raw in (None, ''):
            return None
        try:
            return Decimal(str(raw))
        except (InvalidOperation, ValueError):
            return None

    def form_valid(self, form):
        formset = self.get_formset(self.request.POST)
        item_formset = self.get_item_formset(self.request.POST)
        if not formset.is_valid() or not item_formset.is_valid():
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self._apply_item_rules(form, item_formset)
                self._apply_payment_rules(form, formset)
                response = super().form_valid(form)
                formset.instance = self.object
                formset.save()
                item_formset.instance = self.object
                item_formset.save()

                if not self.object.payments.exists():
                    self.object.payments.create(wallet=self.object.wallet, amount=self.object.amount)

                create_expense_transactions_for_expense(self.object)
                return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['payment_formset'] = self.get_formset(self.request.POST)
            context['item_formset'] = self.get_item_formset(self.request.POST)
        else:
            context['payment_formset'] = self.get_formset()
            context['item_formset'] = self.get_item_formset()
        return context

    def _apply_payment_rules(self, form, formset):
        payments = self._get_payment_forms(formset)
        if not payments:
            raise ValidationError("Add at least one payment wallet.")

        total = Decimal('0.00')
        for payment_form in payments:
            amount = payment_form.cleaned_data.get('amount') or Decimal('0.00')
            total += Decimal(amount)

        remainder = form.cleaned_data['amount'] - total
        if remainder != 0:
            last_form = payments[-1]
            current_amount = last_form.cleaned_data.get('amount') or Decimal('0.00')
            new_amount = current_amount + remainder
            if new_amount < 0:
                raise ValidationError("Split payments exceed the total amount.")
            last_form.cleaned_data['amount'] = new_amount
            last_form.instance.amount = new_amount

        primary_wallet = payments[0].cleaned_data.get('wallet')
        if not primary_wallet:
            raise ValidationError("Add at least one payment wallet.")
        form.instance.wallet = primary_wallet

    def _apply_item_rules(self, form, item_formset):
        items = self._get_item_forms(item_formset)
        if not items:
            return

        total = Decimal('0.00')
        for item_form in items:
            amount = item_form.cleaned_data.get('amount') or Decimal('0.00')
            total += Decimal(amount)

        form.cleaned_data['amount'] = total
        form.instance.amount = total

    def _get_item_forms(self, item_formset):
        forms = []
        for item_form in item_formset.forms:
            if not hasattr(item_form, 'cleaned_data'):
                continue
            if item_form.cleaned_data.get('DELETE'):
                continue
            name = item_form.cleaned_data.get('name')
            amount = item_form.cleaned_data.get('amount')
            if name and amount is not None:
                forms.append(item_form)
        return forms

    def _get_payment_forms(self, formset):
        forms = []
        for payment_form in formset.forms:
            if not hasattr(payment_form, 'cleaned_data'):
                continue
            if payment_form.cleaned_data.get('DELETE'):
                continue
            if payment_form.cleaned_data.get('wallet') is None:
                continue
            forms.append(payment_form)
        return forms

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:list')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_system_generated:
            raise PermissionDenied("System-generated expenses cannot be manually modified or deleted.")
        return super().dispatch(request, *args, **kwargs)

    def get_formset(self, data=None):
        amount = self._get_amount_from_request(data)
        return ExpensePaymentFormSet(
            data,
            instance=self.object,
            prefix='payments',
            expense_amount=amount
        )

    def get_item_formset(self, data=None):
        amount = self._get_amount_from_request(data)
        return ExpenseItemFormSet(
            data,
            instance=self.object,
            prefix='items',
            expense_amount=amount
        )

    def _get_amount_from_request(self, data):
        if not data:
            return self.object.amount if self.object else None
        raw = data.get('amount')
        if raw in (None, ''):
            return None
        try:
            return Decimal(str(raw))
        except (InvalidOperation, ValueError):
            return None

    def form_valid(self, form):
        formset = self.get_formset(self.request.POST)
        item_formset = self.get_item_formset(self.request.POST)
        if not formset.is_valid() or not item_formset.is_valid():
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self._apply_item_rules(form, item_formset)
                self._apply_payment_rules(form, formset)
                response = super().form_valid(form)
                formset.instance = self.object
                formset.save()
                item_formset.instance = self.object
                item_formset.save()

                if not self.object.payments.exists():
                    self.object.payments.create(wallet=self.object.wallet, amount=self.object.amount)

                replace_expense_transactions_for_expense(self.object)
                return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['payment_formset'] = self.get_formset(self.request.POST)
            context['item_formset'] = self.get_item_formset(self.request.POST)
        else:
            context['payment_formset'] = self.get_formset()
            context['item_formset'] = self.get_item_formset()
        return context

    def _apply_payment_rules(self, form, formset):
        payments = self._get_payment_forms(formset)
        if not payments:
            raise ValidationError("Add at least one payment wallet.")

        total = Decimal('0.00')
        for payment_form in payments:
            amount = payment_form.cleaned_data.get('amount') or Decimal('0.00')
            total += Decimal(amount)

        remainder = form.cleaned_data['amount'] - total
        if remainder != 0:
            last_form = payments[-1]
            current_amount = last_form.cleaned_data.get('amount') or Decimal('0.00')
            new_amount = current_amount + remainder
            if new_amount < 0:
                raise ValidationError("Split payments exceed the total amount.")
            last_form.cleaned_data['amount'] = new_amount
            last_form.instance.amount = new_amount

        primary_wallet = payments[0].cleaned_data.get('wallet')
        if not primary_wallet:
            raise ValidationError("Add at least one payment wallet.")
        form.instance.wallet = primary_wallet

    def _apply_item_rules(self, form, item_formset):
        items = self._get_item_forms(item_formset)
        if not items:
            return

        total = Decimal('0.00')
        for item_form in items:
            amount = item_form.cleaned_data.get('amount') or Decimal('0.00')
            total += Decimal(amount)

        form.cleaned_data['amount'] = total
        form.instance.amount = total

    def _get_item_forms(self, item_formset):
        forms = []
        for item_form in item_formset.forms:
            if not hasattr(item_form, 'cleaned_data'):
                continue
            if item_form.cleaned_data.get('DELETE'):
                continue
            name = item_form.cleaned_data.get('name')
            amount = item_form.cleaned_data.get('amount')
            if name and amount is not None:
                forms.append(item_form)
        return forms

    def _get_payment_forms(self, formset):
        forms = []
        for payment_form in formset.forms:
            if not hasattr(payment_form, 'cleaned_data'):
                continue
            if payment_form.cleaned_data.get('DELETE'):
                continue
            if payment_form.cleaned_data.get('wallet') is None:
                continue
            forms.append(payment_form)
        return forms

class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses:list')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_system_generated:
            raise PermissionDenied("System-generated expenses cannot be manually modified or deleted.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        delete_expense_transaction(self.object)
        return super().form_valid(form)


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:list')
