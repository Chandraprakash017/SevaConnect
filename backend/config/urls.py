"""
SevaConnect URL Configuration

All API routes are grouped by app with the /api/ prefix.
"""

from django.urls import path, include

urlpatterns = [
    # Health check - useful to verify server is running
    path('api/health/', include('common.urls')),

    # Authentication (register, login, refresh token)
    path('api/auth/', include('accounts.urls')),

    # Departments and Services (browse)
    path('api/', include('departments.urls')),
    path('api/', include('services.urls')),

    # Bookings (create, view, update status)
    path('api/', include('bookings.urls')),

    # Technician actions (profile, job accept/reject)
    path('api/', include('technicians.urls')),

    # AI Assistant (problem diagnosis)
    path('api/', include('ai_assistant.urls')),

    # Payments
    path('api/', include('payments.urls')),

    # Reviews
    path('api/', include('reviews.urls')),
]
