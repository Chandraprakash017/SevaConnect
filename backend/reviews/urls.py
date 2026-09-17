from django.urls import path
from . import views

urlpatterns = [
    path('bookings/<str:booking_id>/review/', views.create_review, name='create_review'),
    path('bookings/<str:booking_id>/review/me/', views.get_my_review, name='get_my_review'),
    path('technicians/<str:tech_id>/reviews/', views.list_reviews_for_technician, name='technician_reviews'),
]
