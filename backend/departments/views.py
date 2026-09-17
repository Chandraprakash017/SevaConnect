"""
Departments views for SevaConnect.

Departments are the top-level categories (Vehicle, Electrical, etc.)
Each department contains multiple services.
"""

from datetime import datetime
from bson import ObjectId
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([AllowAny])
def list_departments(request):
    """Get all departments. Public endpoint - no login needed."""
    departments = list(db.departments.find({"is_active": True}).sort("order", 1))
    return Response(serialize_list(departments))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_department(request, dept_id):
    """Get a single department by ID."""
    department = db.departments.find_one({"_id": str_to_objectid(dept_id)})
    if not department:
        return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(serialize_doc(department))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_department(request):
    """Admin only: Create a new department."""
    data = request.data

    if not data.get('name'):
        return Response({"error": "'name' is required."}, status=status.HTTP_400_BAD_REQUEST)

    new_department = {
        "name": data['name'].strip(),
        "description": data.get('description', '').strip(),
        "icon": data.get('icon', '🔧'),       # Emoji icon shown on frontend
        "color": data.get('color', '#6366f1'), # Theme color for this department
        "order": data.get('order', 99),        # Display order on homepage
        "is_active": True,
        "created_at": datetime.utcnow(),
    }

    result = db.departments.insert_one(new_department)
    new_department['_id'] = result.inserted_id

    return Response(serialize_doc(new_department), status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_department(request, dept_id):
    """Admin only: Update a department."""
    data = request.data

    update_fields = {}
    allowed_fields = ['name', 'description', 'icon', 'color', 'order', 'is_active']
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    db.departments.update_one(
        {"_id": str_to_objectid(dept_id)},
        {"$set": update_fields}
    )

    updated = db.departments.find_one({"_id": str_to_objectid(dept_id)})
    return Response(serialize_doc(updated))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_department(request, dept_id):
    """Admin only: Soft-delete a department (sets is_active=False)."""
    db.departments.update_one(
        {"_id": str_to_objectid(dept_id)},
        {"$set": {"is_active": False}}
    )
    return Response({"message": "Department deactivated successfully."})
