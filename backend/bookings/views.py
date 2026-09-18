"""
Bookings views for SevaConnect — full implementation.

Booking Status Flow:
  requested → assigned → on_way → inspection → waiting_approval → in_progress → completed
                                                               ↘ cancelled (customer rejects quote)
  Any stage → cancelled (customer/admin only, with restrictions)

Who can do what:
  Customer    : create booking, cancel before assignment, approve/reject quote
  Technician  : accept job, update status (on_way, inspection, waiting_approval, in_progress, completed), add bill
  Admin       : assign technician, cancel any booking
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsCustomer, IsTechnician, IsAdmin

# All valid booking statuses in order
BOOKING_STATUSES = (
    'requested', 'assigned', 'on_way', 'inspection',
    'waiting_approval', 'in_progress', 'completed', 'cancelled'
)


def _add_status_history(booking_id, new_status, note=""):
    """
    Add an entry to the booking's status history.
    This is how the customer sees the timeline on the booking detail page.
    """
    history_entry = {
        "status": new_status,
        "timestamp": datetime.utcnow().isoformat(),
        "note": note,
    }
    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$push": {"status_history": history_entry}}
    )


def _create_invoice(booking):
    """
    Create an invoice document when a booking is completed.
    Called automatically when technician marks booking as 'completed'.
    """
    from invoices.views import generate_invoice_number

    # Build line items for the invoice
    items = []

    visit_charge = booking.get('visit_charge', 0)
    if visit_charge:
        items.append({"description": "Visit Charge", "amount": visit_charge})

    inspection_charge = booking.get('inspection_charge', 0)
    if inspection_charge:
        items.append({"description": "Inspection Charge", "amount": inspection_charge})

    labour_charge = booking.get('labour_charge', 0)
    if labour_charge:
        items.append({"description": "Labour Charges", "amount": labour_charge})

    # Add each part used
    for part in booking.get('parts_used', []):
        total_part_cost = part.get('price', 0) * part.get('quantity', 1)
        items.append({
            "description": part.get('name', 'Part'),
            "quantity": part.get('quantity', 1),
            "unit_price": part.get('price', 0),
            "amount": total_part_cost,
        })

    subtotal = sum(item['amount'] for item in items)

    invoice = {
        "invoice_number": generate_invoice_number(),
        "booking_id": booking['_id'],
        "customer_id": booking.get('customer_id'),
        "technician_id": booking.get('technician_id'),
        "service_name": booking.get('service_name', ''),
        "items": items,
        "subtotal": subtotal,
        "total": subtotal,
        "payment_status": booking.get('payment_status', 'unpaid'),
        "created_at": datetime.utcnow(),
    }

    result = db.invoices.insert_one(invoice)
    return str(result.inserted_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def create_booking(request):
    """
    Customer: Create a new booking request.

    Request body:
    {
        "service_id": "<id>",
        "problem_description": "My bike is not starting",
        "ai_diagnosis_id": "<session_id>",   (optional - from AI assistant)
        "address": "123 Main Street",
        "city": "Mumbai",
        "pincode": "400001",
        "landmark": "Near Reliance petrol pump",
        "scheduled_date": "2024-12-25",
        "scheduled_time": "10:00 AM"
    }
    """
    user = request.user
    data = request.data

    required = ['service_id', 'problem_description', 'address', 'city', 'pincode', 'scheduled_date', 'scheduled_time']
    for field in required:
        if not data.get(field):
            return Response({"error": f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    service_oid = str_to_objectid(data['service_id'])
    if not service_oid:
        return Response({"error": "Invalid service_id."}, status=status.HTTP_400_BAD_REQUEST)

    # Get service details including pricing
    service = db.services.find_one({"_id": service_oid, "is_active": True})
    if not service:
        return Response({"error": "Service not found or unavailable."}, status=status.HTTP_404_NOT_FOUND)

    # Get AI diagnosis if customer used the assistant
    ai_diagnosis = None
    if data.get('ai_diagnosis_id'):
        ai_session = db.ai_diagnosis.find_one({"_id": str_to_objectid(data['ai_diagnosis_id'])})
        if ai_session:
            ai_diagnosis = ai_session.get('final_diagnosis') or ai_session.get('initial_diagnosis', {}).get('initial_diagnosis')

    new_booking = {
        "customer_id": str_to_objectid(user.id),
        "service_id": service_oid,
        "service_name": service.get('name', ''),
        "problem_description": data['problem_description'].strip(),
        "ai_diagnosis_id": str_to_objectid(data.get('ai_diagnosis_id')) if data.get('ai_diagnosis_id') else None,
        "ai_diagnosis_summary": ai_diagnosis,   # Saved here for technician to see

        # Location
        "address": data['address'].strip(),
        "city": data['city'].strip(),
        "pincode": data['pincode'].strip(),
        "landmark": data.get('landmark', '').strip(),

        # Schedule
        "scheduled_date": data['scheduled_date'],
        "scheduled_time": data['scheduled_time'],

        # Pricing (from service configuration)
        "visit_charge": service.get('visit_charge', 100),
        "inspection_charge": service.get('inspection_charge', 50),
        "estimated_min": service.get('labour_min', 0) + service.get('visit_charge', 100),
        "estimated_max": service.get('labour_max', 0) + service.get('visit_charge', 100),

        # Technician will fill these after inspection
        "technician_id": None,
        "labour_charge": 0,
        "parts_used": [],
        "final_price": 0,
        "technician_notes": "",

        # Status
        "status": "requested",
        "payment_status": "unpaid",
        "status_history": [{"status": "requested", "timestamp": datetime.utcnow().isoformat(), "note": "Booking created"}],

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
    Get bookings for the current user.
    - Customers see their own bookings
    - Technicians see their assigned jobs
    - Admin sees all bookings
    Optional filter: ?status=requested
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

    # Status filter
    status_filter = request.query_params.get('status', '').strip()
    if status_filter in BOOKING_STATUSES:
        query['status'] = status_filter

    bookings = list(db.bookings.find(query).sort("created_at", -1))
    return Response(serialize_list(bookings))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_available_jobs(request):
    """
    Technician: See bookings that are 'requested' and not yet assigned.
    Technicians can browse these and accept jobs.

    Filter by city/pincode to see nearby jobs.
    """
    query = {"status": "requested", "technician_id": None}

    city = request.query_params.get('city', '').strip()
    if city:
        query['city'] = {"$regex": city, "$options": "i"}

    pincode = request.query_params.get('pincode', '').strip()
    if pincode:
        query['pincode'] = pincode

    jobs = list(db.bookings.find(query).sort("created_at", -1))
    return Response(serialize_list(jobs))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking(request, booking_id):
    """Get full details of a single booking."""
    user = request.user
    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})

    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access control
    if user.role == 'customer' and str(booking.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    if user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech or str(booking.get('technician_id')) != str(tech['_id']):
            # Technician can also view unassigned jobs before accepting
            if booking.get('status') != 'requested' or booking.get('technician_id') is not None:
                return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    return Response(serialize_doc(booking))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTechnician])
def accept_job(request, booking_id):
    """
    Technician: Accept an unassigned booking.
    This assigns the technician and moves status to 'assigned'.
    """
    user = request.user

    tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
    if not tech:
        return Response({"error": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    if booking.get('status') != 'requested':
        return Response({"error": "This booking is no longer available."}, status=status.HTTP_400_BAD_REQUEST)

    if booking.get('technician_id') is not None:
        return Response({"error": "This booking has already been assigned."}, status=status.HTTP_400_BAD_REQUEST)

    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {
            "technician_id": tech['_id'],
            "status": "assigned",
            "updated_at": datetime.utcnow(),
        }}
    )
    _add_status_history(booking_id, "assigned", f"Technician {user.name} accepted the job")

    # Update technician's total jobs count
    db.technicians.update_one({"_id": tech['_id']}, {"$inc": {"total_jobs": 1}})

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTechnician])
def reject_job(request, booking_id):
    """
    Technician: Reject a job they were directly assigned to.
    This resets the booking back to 'requested' with no technician.
    """
    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    tech = db.technicians.find_one({"user_id": str_to_objectid(request.user.id)})
    if not tech or str(booking.get('technician_id')) != str(tech['_id']):
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {
            "technician_id": None,
            "status": "requested",
            "updated_at": datetime.utcnow(),
        }}
    )
    _add_status_history(booking_id, "requested", "Technician rejected. Looking for another technician.")

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_status(request, booking_id):
    """
    Update booking status. Each role has allowed transitions only.

    Body: {"status": "on_way", "note": "I am on the way"}
    """
    user = request.user
    new_status = request.data.get('status', '').strip()
    note = request.data.get('note', '')

    if new_status not in BOOKING_STATUSES:
        return Response(
            {"error": f"Invalid status. Choose from: {', '.join(BOOKING_STATUSES)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    current = booking.get('status')

    # Define what each role is allowed to do
    if user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech or str(booking.get('technician_id')) != str(tech['_id']):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        allowed = {
            'assigned': ['on_way'],
            'on_way': ['inspection'],
            'inspection': ['waiting_approval'],
            'in_progress': ['completed'],
        }
        if new_status not in allowed.get(current, []):
            return Response(
                {"error": f"Cannot move from '{current}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    elif user.role == 'customer':
        if str(booking.get('customer_id')) != user.id:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        # Customer can only cancel before assignment, or approve/reject quote
        allowed = {
            'requested': ['cancelled'],
            'waiting_approval': ['in_progress', 'cancelled'],
        }
        if new_status not in allowed.get(current, []):
            return Response(
                {"error": f"You cannot change the status from '{current}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Admin can set any status
    elif user.role != 'admin':
        return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )
    _add_status_history(booking_id, new_status, note)

    # If job is completed, generate invoice automatically
    if new_status == 'completed':
        updated_booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
        invoice_id = _create_invoice(updated_booking)
        db.bookings.update_one(
            {"_id": str_to_objectid(booking_id)},
            {"$set": {"invoice_id": str_to_objectid(invoice_id)}}
        )

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTechnician])
def submit_quote(request, booking_id):
    """
    Technician: After inspection, submit the repair quote.
    This moves the booking to 'waiting_approval' so the customer can approve.

    Request body:
    {
        "labour_charge": 300,
        "parts_used": [
            {"name": "Bike Battery", "quantity": 1, "price": 1400},
            {"name": "Spark Plug", "quantity": 1, "price": 150}
        ],
        "technician_notes": "Battery is dead, spark plug also worn out"
    }
    """
    user = request.user
    data = request.data

    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only the assigned technician can submit a quote
    tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
    if not tech or str(booking.get('technician_id')) != str(tech['_id']):
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    if booking.get('status') != 'inspection':
        return Response({"error": "Quote can only be submitted during inspection."}, status=status.HTTP_400_BAD_REQUEST)

    labour_charge = float(data.get('labour_charge', 0))
    parts_used = data.get('parts_used', [])

    # Calculate the total parts cost
    parts_total = sum(p.get('price', 0) * p.get('quantity', 1) for p in parts_used)

    # Final price = visit + inspection + labour + parts
    final_price = (
        booking.get('visit_charge', 0) +
        booking.get('inspection_charge', 0) +
        labour_charge +
        parts_total
    )

    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {
            "labour_charge": labour_charge,
            "parts_used": parts_used,
            "final_price": final_price,
            "technician_notes": data.get('technician_notes', '').strip(),
            "status": "waiting_approval",
            "updated_at": datetime.utcnow(),
        }}
    )
    _add_status_history(booking_id, "waiting_approval", f"Quote submitted: ₹{final_price}")

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_technician(request, booking_id):
    """Admin: Manually assign a technician to a booking."""
    tech_id = request.data.get('technician_id')
    if not tech_id:
        return Response({"error": "'technician_id' is required."}, status=status.HTTP_400_BAD_REQUEST)

    tech = db.technicians.find_one({"_id": str_to_objectid(tech_id), "is_verified": True})
    if not tech:
        return Response({"error": "Technician not found or not verified."}, status=status.HTTP_404_NOT_FOUND)

    result = db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {
            "technician_id": tech['_id'],
            "status": "assigned",
            "updated_at": datetime.utcnow(),
        }}
    )

    if result.matched_count == 0:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    _add_status_history(booking_id, "assigned", "Technician assigned by admin")

    updated = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    return Response(serialize_doc(updated))
