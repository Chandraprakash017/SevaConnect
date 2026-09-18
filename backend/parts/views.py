"""
Parts views for SevaConnect.

Parts are the components/items a technician might use during repair.
Admin manages the catalog. Technicians pick from this list when adding to a job.

Examples: Bike Battery, Spark Plug, AC Filter, MCB Switch, etc.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([AllowAny])
def list_parts(request):
    """
    List all active parts. Optionally filter by category.
    This is public so the AI can suggest parts to customers.

    Query params:
        ?category=Vehicle    - filter by category
        ?search=battery      - search by name
    """
    query = {"is_active": True}

    category = request.query_params.get('category', '').strip()
    if category:
        query['category'] = {"$regex": category, "$options": "i"}

    search = request.query_params.get('search', '').strip()
    if search:
        query['name'] = {"$regex": search, "$options": "i"}

    parts = list(db.parts.find(query).sort("name", 1))
    return Response(serialize_list(parts))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_part(request, part_id):
    """Get a single part by ID."""
    part = db.parts.find_one({"_id": str_to_objectid(part_id)})
    if not part:
        return Response({"error": "Part not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(serialize_doc(part))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_part(request):
    """
    Admin only: Add a new part to the catalog.

    Expected body:
    {
        "name": "Bike Battery",
        "category": "Vehicle",
        "description": "Lead acid battery for bikes",
        "min_price": 1200,
        "max_price": 2000,
        "unit": "piece",
        "stock": 10
    }
    """
    data = request.data

    required = ['name', 'category', 'min_price', 'max_price']
    for field in required:
        if not data.get(field) and data.get(field) != 0:
            return Response({"error": f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    new_part = {
        "name": data['name'].strip(),
        "category": data['category'].strip(),
        "description": data.get('description', '').strip(),
        "min_price": float(data['min_price']),
        "max_price": float(data['max_price']),
        "unit": data.get('unit', 'piece'),   # piece / metre / litre
        "stock": int(data.get('stock', 0)),
        "is_active": True,
        "created_at": datetime.utcnow(),
    }

    result = db.parts.insert_one(new_part)
    new_part['_id'] = result.inserted_id

    return Response(serialize_doc(new_part), status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_part(request, part_id):
    """Admin only: Update a part's details or stock."""
    data = request.data

    update_fields = {}
    allowed_fields = ['name', 'category', 'description', 'min_price', 'max_price', 'unit', 'stock', 'is_active']
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    result = db.parts.update_one(
        {"_id": str_to_objectid(part_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return Response({"error": "Part not found."}, status=status.HTTP_404_NOT_FOUND)

    updated = db.parts.find_one({"_id": str_to_objectid(part_id)})
    return Response(serialize_doc(updated))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_part(request, part_id):
    """Admin only: Soft-delete a part (marks as inactive)."""
    result = db.parts.update_one(
        {"_id": str_to_objectid(part_id)},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        return Response({"error": "Part not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"message": "Part deactivated successfully."})
