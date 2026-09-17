from django.urls import path
from . import views

urlpatterns = [
    # Customer: create a booking
    path('bookings/', views.list_my_bookings, name='list_my_bookings'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/<str:booking_id>/', views.get_booking, name='get_booking'),
    path('bookings/<str:booking_id>/status/', views.update_booking_status, name='update_booking_status'),
    path('bookings/<str:booking_id>/assign/', views.assign_technician, name='assign_technician'),
]
