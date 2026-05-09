from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.VendorListView.as_view(), name='list'),
    path('add/', views.VendorCreateView.as_view(), name='add'),
]
