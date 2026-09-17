"""
Payments views for SevaConnect.

Uses Razorpay for payment processing.

Flow:
  1. Customer calls /payments/create-order/ → gets a Razorpay order_id
  2. Frontend opens Razorpay checkout with that order_id
  3. On success, frontend sends payment_id + signature to /payments/verify/
  4. Backend verifies the signature and marks the booking as paid
"""

import hmac
import hashlib
import razorpay
from datetime import datetime

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, str_to_objectid
from common.permissions import IsCustomer


def _get_razorpay_client():
    """Return an authenticated Razorpay client."""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def create_payment_order(request, booking_id):
    """
    Customer: Create a Razorpay payment order for a booking.

    Returns the Razorpay order details that the frontend needs to
    open the checkout modal.
    """
    user = request.user

    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only the booking's customer can pay
    if str(booking.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    # Don't create a new order if already paid
    if booking.get('payment_status') == 'paid':
        return Response({"error": "This booking has already been paid."}, status=status.HTTP_400_BAD_REQUEST)

    # Razorpay amount is in paise (INR × 100)
    amount_paise = int(booking.get('base_price', 0) * 100)
    if amount_paise <= 0:
        return Response({"error": "Booking has no valid price."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        client = _get_razorpay_client()
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": str(booking['_id']),
            "notes": {
                "booking_id": str(booking['_id']),
                "customer_id": user.id,
                "service": booking.get('service_name', ''),
            }
        })
    except Exception as e:
        return Response(
            {"error": f"Failed to create Razorpay order: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # Save the Razorpay order ID to the booking for later verification
    db.bookings.update_one(
        {"_id": str_to_objectid(booking_id)},
        {"$set": {"razorpay_order_id": order['id'], "updated_at": datetime.utcnow()}}
    )

    return Response({
        "order_id": order['id'],
        "amount": amount_paise,
        "currency": "INR",
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "booking_id": str(booking['_id']),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def verify_payment(request):
    """
    Customer: Verify a Razorpay payment after checkout.

    Razorpay sends a signature that we verify using HMAC-SHA256.
    If valid, we mark the booking as paid.

    Expected body:
    {
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "signature_string",
        "booking_id": "<booking_id>"
    }
    """
    data = request.data

    required = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'booking_id']
    for field in required:
        if not data.get(field):
            return Response({"error": f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the Razorpay signature
    msg = f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}"
    expected_signature = hmac.new(
        key=settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
        msg=msg.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if expected_signature != data['razorpay_signature']:
        return Response({"error": "Invalid payment signature."}, status=status.HTTP_400_BAD_REQUEST)

    # Mark booking as paid
    db.bookings.update_one(
        {"_id": str_to_objectid(data['booking_id'])},
        {"$set": {
            "payment_status": "paid",
            "razorpay_payment_id": data['razorpay_payment_id'],
            "paid_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }}
    )

    return Response({"message": "Payment verified successfully. Booking is now paid."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, booking_id):
    """
    Get the payment status of a booking.
    Customer can check their own; admins can check any.
    """
    user = request.user
    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})

    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    if user.role == 'customer' and str(booking.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        "booking_id": str(booking['_id']),
        "payment_status": booking.get('payment_status', 'unpaid'),
        "razorpay_order_id": booking.get('razorpay_order_id'),
        "razorpay_payment_id": booking.get('razorpay_payment_id'),
        "paid_at": booking.get('paid_at').isoformat() if booking.get('paid_at') else None,
        "amount": booking.get('base_price', 0),
    })
