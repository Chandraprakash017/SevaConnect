"""
Bookings views for SevaConnect.

Booking lifecycle:
  pending → accepted → in_progress → completed
                     ↘ rejected
  (can also be cancelled by customer before acceptance)

Customer creates a booking → technician accepts/rejects →
technician marks in_progress → technician marks completed.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsCustomer, IsTechnician, IsAdmin

# Valid booking statuses
VALID_STATUSES = ('pending', 'accepted', 'rejected', 'in_progress', 'completed', 'cancelled')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def create_booking(request):
    """
    Customer: Create a new service booking.

    Expected body:
    {
        "service_id": "<service_id>",
        "technician_id": "<technician_id>",  (optional — auto-assign if not provided)
        "scheduled_date": "2024-12-25",
        "scheduled_time": "10:00",
        "address": "123 Main Street, Mumbai",
        "notes": "Please bring your own tools"
    }
    """
    user = request.user
    data = request.data

    required = ['service_id', 'scheduled_date', 'scheduled_time', 'address']
    for field in required:
        if not data.get(field):
            return Response({"error": f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    service_oid = str_to_objectid(data['service_id'])
    if not service_oid:
        return Response({"error": "Invalid service_id."}, status=status.HTTP_400_BAD_REQUEST)

    service = db.services.find_one({"_id": service_oid, "is_active": True})
    if not service:
        return Response({"error": "Service not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

    technician_oid = None
    if data.get('technician_id'):
        technician_oid = str_to_objectid(data['technician_id'])
        tech = db.technicians.find_one({"_id": technician_oid, "is_verified": True})
        if not tech:
            return Response({"error": "Technician not found or not verified."}, status=status.HTTP_404_NOT_FOUND)

    new_booking = {
        "customer_id": str_to_objectid(user.id),
        "service_id": service_oid,
        "technician_id": technician_oid,          # None means auto-assign
        "service_name": service.get('name', ''),
        "base_price": service.get('base_price', 0),
        "scheduled_date": data['scheduled_date'],
        "scheduled_time": data['scheduled_time'],
        "address": data['address'].strip(),
        "notes": data.get('notes', '').strip(),
        "status": "pending",
        "payment_status": "unpaid",               # unpaid | paid
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = db.bookings.insert_one(new_booking)
    new_booking['_id'] = result.inserted_id

    return Response(serialize_doc(new_booking), status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_bookings(request):
    """
    Customer or Technician: List your own bookings.

    Query params:
        ?status=pending     - filter by status
    """
    user = request.user
    query = {}

    if user.role == 'customer':
        query['customer_id'] = str_to_objectid(user.id)
    elif user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech:
            return Response({"error": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)
        query['technician_id'] = tech['_id']
    elif user.role == 'admin':
        pass  # Admin sees all bookings

    status_filter = request.query_params.get('status', '').strip()
    if status_filter and status_filter in VALID_STATUSES:
        query['status'] = status_filter

    bookings = list(db.bookings.find(query).sort("created_at", -1))
    return Response(serialize_list(bookings))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking(request, booking_id):
    """Get a single booking's details."""
    user = request.user
    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})

    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access control: only the customer, assigned technician, or admin can view
    if user.role == 'customer' and str(booking.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    if user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech or str(booking.get('technician_id')) != str(tech['_id']):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    return Response(serialize_doc(booking))


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_booking_status(request, booking_id):
    """
    Update the status of a booking.

    - Technician can: accept, reject, mark in_progress, complete
    - Customer can: cancel (only when status is 'pending')
    - Admin can set any status

    Body: {"status": "accepted"}
    """
    user = request.user
    new_status = request.data.get('status', '').strip()

    if new_status not in VALID_STATUSES:
        return Response(
            {"error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    current_status = booking.get('status')

    # Permission checks based on role
    if user.role == 'customer':
        if str(booking.get('customer_id')) != user.id:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        if new_status != 'cancelled' or current_status != 'pending':
            return Response(
                {"error": "Customers can only cancel pending bookings."},
                status=status.HTTP_403_FORBIDDEN
            )

    elif user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech or str(booking.get('technician_id')) != str(tech['_id']):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        allowed_transitions = {
            'pending': ['accepted', 'rejected'],
            'accepted': ['in_progress'],
            'in_progress': ['completed'],
        }
        allowed = allowed_transitions.get(current_status, [])
        if new_status not in allowed:
            return Response(
                {"error": f"Cannot transition from '{current_status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    update_data = {
        "status": new_status,
        "updated_at": datetime.utcnow(),
    }

    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": update_data}
    )

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_technician(request, booking_id):
    """
    Admin only: Assign a technician to a pending booking.
    Body: {"technician_id": "<technician_id>"}
    """
    tech_id = request.data.get('technician_id')
    if not tech_id:
        return Response({"error": "'technician_id' is required."}, status=status.HTTP_400_BAD_REQUEST)

    tech = db.technicians.find_one({"_id": str_to_objectid(tech_id), "is_verified": True})
    if not tech:
        return Response({"error": "Technician not found or not verified."}, status=status.HTTP_404_NOT_FOUND)

    result = db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {"technician_id": tech['_id'], "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))
