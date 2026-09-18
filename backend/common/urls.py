from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
]
