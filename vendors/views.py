from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Vendor

class VendorListView(ListView):
    model = Vendor
    template_name = 'vendors/vendor_list.html'
    context_object_name = 'vendors'
    ordering = ['-created_at']

class VendorCreateView(CreateView):
    model = Vendor
    fields = ['name', 'contact']
    template_name = 'vendors/vendor_form.html'
    success_url = reverse_lazy('vendors:list')
