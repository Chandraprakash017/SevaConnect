"""
Custom permission classes for SevaConnect.

These are used on API views to restrict access by role.

Example usage in a view:
    from common.permissions import IsCustomer, IsTechnician, IsAdmin

    class BookingCreateView(APIView):
        permission_classes = [IsAuthenticated, IsCustomer]
"""

from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Only allow users with role 'customer' to access this view."""

    message = "Only customers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'customer'
        )


class IsTechnician(BasePermission):
    """Only allow users with role 'technician' to access this view."""

    message = "Only technicians can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'technician'
        )


class IsAdmin(BasePermission):
    """Only allow users with role 'admin' to access this view."""

    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'admin'
        )


class IsCustomerOrAdmin(BasePermission):
    """Allow customers or admins - useful for read operations."""

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return (
            request.user
            and request.user.is_authenticated
            and role in ('customer', 'admin')
        )


class IsTechnicianOrAdmin(BasePermission):
    """Allow technicians or admins."""

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return (
            request.user
            and request.user.is_authenticated
            and role in ('technician', 'admin')
        )
