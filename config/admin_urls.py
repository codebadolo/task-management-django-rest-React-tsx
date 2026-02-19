# config/admin_urls.py
from django.contrib import admin
from django.urls import path

def get_admin_urls():
    """Retourne les URLs admin de manière différée"""
    return [
        path('admin/', admin.site.urls),
    ]