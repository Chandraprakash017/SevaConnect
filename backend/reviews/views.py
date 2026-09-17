"""
Reviews views for SevaConnect.

Customers can leave a review after a booking is completed.
Each review has a rating (1–5 stars) and optional text.
Technician's average rating is updated automatically on each review.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsCustomer


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def create_review(request, booking_id):
    """
    Customer: Submit a review for a completed booking.

    Can only review ONCE per booking, and only if status is 'completed'.

    Expected body:
    {
        "rating": 5,          (integer 1–5)
        "comment": "Great work!"
    }
    """
    user = request.user
    data = request.data

    rating = data.get('rating')
    if rating is None:
        return Response({"error": "'rating' is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        return Response({"error": "'rating' must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    if not (1 <= rating <= 5):
        return Response({"error": "'rating' must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the booking
    booking = db.bookings.find_one({"_id": str_to_objectid(booking_id)})
    if not booking:
        return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only the customer who made the booking can review it
    if str(booking.get('customer_id')) != user.id:
        return Response({"error": "You can only review your own bookings."}, status=status.HTTP_403_FORBIDDEN)

    # Booking must be completed to leave a review
    if booking.get('status') != 'completed':
        return Response({"error": "You can only review completed bookings."}, status=status.HTTP_400_BAD_REQUEST)

    # Only one review per booking
    existing_review = db.reviews.find_one({"booking_id": str_to_objectid(booking_id)})
    if existing_review:
        return Response({"error": "You have already reviewed this booking."}, status=status.HTTP_409_CONFLICT)

    technician_id = booking.get('technician_id')
    new_review = {
        "booking_id": str_to_objectid(booking_id),
        "customer_id": str_to_objectid(user.id),
        "technician_id": technician_id,
        "rating": rating,
        "comment": data.get('comment', '').strip(),
        "created_at": datetime.utcnow(),
    }

    db.reviews.insert_one(new_review)

    # Update the technician's average rating
    if technician_id:
        _update_technician_rating(technician_id)

    return Response(serialize_doc(new_review), status=status.HTTP_201_CREATED)


def _update_technician_rating(technician_id):
    """
    Recalculate and update a technician's average rating.
    Called internally after a new review is submitted.
    """
    pipeline = [
        {"$match": {"technician_id": technician_id}},
        {"$group": {
            "_id": "$technician_id",
            "avg_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    result = list(db.reviews.aggregate(pipeline))

    if result:
        avg = round(result[0]['avg_rating'], 2)
        total = result[0]['total_reviews']
        db.technicians.update_one(
            {"_id": technician_id},
            {"$set": {"ratings_avg": avg, "total_reviews": total}}
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_reviews_for_technician(request, tech_id):
    """
    Public: List all reviews for a specific technician.
    """
    tech_oid = str_to_objectid(tech_id)
    if not tech_oid:
        return Response({"error": "Invalid technician ID."}, status=status.HTTP_400_BAD_REQUEST)

    reviews = list(db.reviews.find({"technician_id": tech_oid}).sort("created_at", -1))

    # Enrich with customer name
    result = []
    for review in reviews:
        review_data = serialize_doc(review)
        customer = db.users.find_one({"_id": review.get('customer_id')})
        if customer:
            review_data['customer_name'] = customer.get('name', 'Anonymous')
        result.append(review_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_review(request, booking_id):
    """Customer: Check if you've already reviewed a booking."""
    review = db.reviews.find_one({"booking_id": str_to_objectid(booking_id)})
    if not review:
        return Response({"reviewed": False, "review": None})
    return Response({"reviewed": True, "review": serialize_doc(review)})
