from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls), # Renamed to avoid conflict with our admin dashboard
    path('', include('nssapp.urls')),
]
