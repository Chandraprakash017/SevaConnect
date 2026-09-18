from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from common.db import db
from common.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint.
    Also verifies that MongoDB connection is working.
    """
    try:
        # Try a simple MongoDB ping to verify connection
        db.command('ping')
        mongo_status = "connected"
    except Exception:
        mongo_status = "disconnected"

    return Response({
        "status": "ok",
        "message": "SevaConnect API is running",
        "mongodb": mongo_status,
        "version": "1.0.0"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_stats(request):
    """
    Admin: Get platform-wide statistics for the admin dashboard.
    Shows totals that help admin understand platform usage at a glance.
    """
    # Count users by role
    total_customers = db.users.count_documents({"role": "customer"})
    total_technicians = db.users.count_documents({"role": "technician"})

    # Booking stats
    total_bookings = db.bookings.count_documents({})
    pending_bookings = db.bookings.count_documents({"status": {"$in": ["requested", "assigned", "on_way", "inspection", "waiting_approval", "in_progress"]}})
    completed_bookings = db.bookings.count_documents({"status": "completed"})
    cancelled_bookings = db.bookings.count_documents({"status": "cancelled"})

    # Revenue: sum of final_price for completed bookings
    revenue_pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$final_price"}}}
    ]
    revenue_result = list(db.bookings.aggregate(revenue_pipeline))
    total_revenue = revenue_result[0]['total'] if revenue_result else 0

    # Reviews
    total_reviews = db.reviews.count_documents({})

    return Response({
        "users": {
            "customers": total_customers,
            "technicians": total_technicians,
        },
        "bookings": {
            "total": total_bookings,
            "pending": pending_bookings,
            "completed": completed_bookings,
            "cancelled": cancelled_bookings,
        },
        "revenue": total_revenue,
        "reviews": total_reviews,
    })
