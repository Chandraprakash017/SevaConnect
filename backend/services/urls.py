from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.list_services, name='list_services'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/<str:service_id>/', views.get_service, name='get_service'),
    path('services/<str:service_id>/update/', views.update_service, name='update_service'),
    path('services/<str:service_id>/delete/', views.delete_service, name='delete_service'),
]
