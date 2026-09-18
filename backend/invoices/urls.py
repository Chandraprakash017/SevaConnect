from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.list_my_invoices, name='list_my_invoices'),
    path('invoices/<str:invoice_id>/', views.get_invoice, name='get_invoice'),
    path('bookings/<str:booking_id>/invoice/', views.get_invoice_by_booking, name='booking_invoice'),
]
