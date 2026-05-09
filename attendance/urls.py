from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceListView.as_view(), name='list'),
    path('export/', views.AttendanceExportView.as_view(), name='export'),
    path('add/', views.AttendanceCreateView.as_view(), name='create'),
    path('work-types/new/', views.WorkTypeCreateView.as_view(), name='worktype_create'),
    path('<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='delete'),
    path('api/wage/', views.get_work_type_wage, name='api_wage'),
]
