from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('expenses/', include('expenses.urls')),
    path('wallets/', include('wallets.urls')),
    path('vendors/', include('vendors.urls')),
    path('attendance/', include('attendance.urls')),
    path('contractors/', include('contractors.urls')),
]
