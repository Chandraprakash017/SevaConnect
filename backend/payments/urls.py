from django.urls import path
from . import views

urlpatterns = [
    path('bookings/<str:booking_id>/payment/create/', views.create_payment_order, name='create_payment_order'),
    path('bookings/<str:booking_id>/payment/status/', views.get_payment_status, name='payment_status'),
    path('payments/verify/', views.verify_payment, name='verify_payment'),
]
