from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.ContractorListView.as_view(), name='list'),
    path('new/', views.ContractorCreateView.as_view(), name='create'),
    path('payments/', views.ContractorPaymentListView.as_view(), name='payments'),
    path('payments/new/', views.ContractorPaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/edit/', views.ContractorPaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', views.ContractorPaymentDeleteView.as_view(), name='payment_delete'),
]
