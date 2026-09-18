from django.urls import path
from . import views

urlpatterns = [
    # Customer: browse and create bookings
    path('bookings/', views.list_my_bookings, name='list_my_bookings'),
    path('bookings/create/', views.create_booking, name='create_booking'),

    # Technician: see available unassigned jobs in their area
    path('bookings/available/', views.list_available_jobs, name='list_available_jobs'),

    # Specific booking actions
    path('bookings/<str:booking_id>/', views.get_booking, name='get_booking'),
    path('bookings/<str:booking_id>/status/', views.update_status, name='update_status'),
    path('bookings/<str:booking_id>/accept/', views.accept_job, name='accept_job'),
    path('bookings/<str:booking_id>/reject/', views.reject_job, name='reject_job'),
    path('bookings/<str:booking_id>/quote/', views.submit_quote, name='submit_quote'),
    path('bookings/<str:booking_id>/assign/', views.assign_technician, name='assign_technician'),
]
