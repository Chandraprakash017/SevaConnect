from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from common.db import db


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
