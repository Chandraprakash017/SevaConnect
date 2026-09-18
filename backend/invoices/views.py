"""
Invoices views for SevaConnect.

An invoice is automatically created when a technician marks a booking as completed.
It contains the breakdown: visit charge, inspection, labour, and parts used.

Customers and technicians can view invoices. Customers can also print/download them.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid


def generate_invoice_number():
    """
    Generate a unique invoice number like SEVA-2024-00142.
    We use the total count of invoices to create a sequential number.
    """
    count = db.invoices.count_documents({})
    year = datetime.utcnow().year
    return f"SEVA-{year}-{str(count + 1).zfill(5)}"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoice(request, invoice_id):
    """
    Get a single invoice by ID.
    Only the customer or technician of the related booking can view it.
    """
    user = request.user
    invoice = db.invoices.find_one({"_id": str_to_objectid(invoice_id)})

    if not invoice:
        return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access check: only the involved customer, technician, or admin
    if user.role == 'customer' and str(invoice.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    if user.role == 'technician':
        tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
        if not tech or str(invoice.get('technician_id')) != str(tech['_id']):
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    return Response(serialize_doc(invoice))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoice_by_booking(request, booking_id):
    """Get the invoice for a specific booking."""
    user = request.user
    invoice = db.invoices.find_one({"booking_id": str_to_objectid(booking_id)})

    if not invoice:
        return Response({"error": "No invoice found for this booking."}, status=status.HTTP_404_NOT_FOUND)

    # Access check
    if user.role == 'customer' and str(invoice.get('customer_id')) != user.id:
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    return Response(serialize_doc(invoice))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_invoices(request):
    """
    List all invoices for the logged-in user.
    Customers see their own invoices. Technicians see invoices they generated.
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
    # Admins see all invoices (no filter)

    invoices = list(db.invoices.find(query).sort("created_at", -1))
    return Response(serialize_list(invoices))
