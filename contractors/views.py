from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Contractor, ContractorPayment
from .forms import ContractorForm, ContractorPaymentForm
from .services import create_contractor_payment, update_contractor_payment, delete_contractor_payment


class ContractorListView(ListView):
	model = Contractor
	template_name = 'contractors/contractor_list.html'
	context_object_name = 'contractors'
	ordering = ['name']


class ContractorCreateView(CreateView):
	model = Contractor
	form_class = ContractorForm
	template_name = 'contractors/contractor_form.html'
	success_url = reverse_lazy('contractors:list')


class ContractorPaymentListView(ListView):
	model = ContractorPayment
	template_name = 'contractors/payment_list.html'
	context_object_name = 'payments'
	ordering = ['-date', '-created_at']


class ContractorPaymentCreateView(CreateView):
	model = ContractorPayment
	form_class = ContractorPaymentForm
	template_name = 'contractors/payment_form.html'
	success_url = reverse_lazy('contractors:payments')

	def form_valid(self, form):
		try:
			create_contractor_payment(form.cleaned_data)
			return HttpResponseRedirect(self.success_url)
		except Exception as exc:
			form.add_error(None, str(exc))
			return self.form_invalid(form)


class ContractorPaymentUpdateView(UpdateView):
	model = ContractorPayment
	form_class = ContractorPaymentForm
	template_name = 'contractors/payment_form.html'
	success_url = reverse_lazy('contractors:payments')

	def form_valid(self, form):
		try:
			payment = self.get_object()
			update_contractor_payment(payment, form.cleaned_data)
			return HttpResponseRedirect(self.success_url)
		except Exception as exc:
			form.add_error(None, str(exc))
			return self.form_invalid(form)


class ContractorPaymentDeleteView(DeleteView):
	model = ContractorPayment
	template_name = 'contractors/payment_confirm_delete.html'
	success_url = reverse_lazy('contractors:payments')

	def form_valid(self, form):
		payment = self.get_object()
		delete_contractor_payment(payment)
		return HttpResponseRedirect(self.success_url)
