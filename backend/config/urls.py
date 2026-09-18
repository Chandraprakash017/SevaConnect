"""
SevaConnect URL Configuration — All API routes.

Each app is mounted under /api/ with a logical prefix.
"""

from django.urls import path, include

urlpatterns = [
    # Health check
    path('api/health/', include('common.urls')),

    # Authentication (register, login, token refresh, profile)
    path('api/auth/', include('accounts.urls')),

    # Service catalog (departments and services)
    path('api/', include('departments.urls')),
    path('api/', include('services.urls')),

    # Parts catalog
    path('api/', include('parts.urls')),

    # Bookings — core flow
    path('api/', include('bookings.urls')),

    # Technician management
    path('api/', include('technicians.urls')),

    # AI problem assistant
    path('api/', include('ai_assistant.urls')),

    # Payments (Razorpay)
    path('api/', include('payments.urls')),

    # Reviews
    path('api/', include('reviews.urls')),

    # Invoices
    path('api/', include('invoices.urls')),
]
