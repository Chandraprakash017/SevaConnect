from django.urls import path
from . import views

urlpatterns = [
    # Technician's own profile
    path('technicians/me/', views.get_my_profile, name='technician_my_profile'),
    path('technicians/me/update/', views.update_my_profile, name='technician_update_profile'),

    # Public listing
    path('technicians/', views.list_technicians, name='list_technicians'),
    path('technicians/<str:tech_id>/', views.get_technician, name='get_technician'),

    # Admin: verify a technician
    path('technicians/<str:tech_id>/verify/', views.verify_technician, name='verify_technician'),
]
