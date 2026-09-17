"""
Services views for SevaConnect.

Services belong to a Department (e.g., 'AC Repair' under 'Electrical').
Each service has a base price, estimated duration, and is linked to technicians.
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
def list_services(request):
    """
    List all active services. Optionally filter by department ID.

    Query params:
        ?dept_id=<department_id>   - filter by department
        ?search=<keyword>          - search by name/description
    """
    query = {"is_active": True}

    dept_id = request.query_params.get('dept_id')
    if dept_id:
        dept_oid = str_to_objectid(dept_id)
        if dept_oid:
            query["dept_id"] = dept_oid

    search = request.query_params.get('search', '').strip()
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]

    services = list(db.services.find(query).sort("name", 1))
    return Response(serialize_list(services))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service(request, service_id):
    """Get a single service by its ID."""
    service = db.services.find_one({"_id": str_to_objectid(service_id)})
    if not service:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(serialize_doc(service))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_service(request):
    """
    Admin only: Create a new service under a department.

    Expected body:
    {
        "dept_id": "<department_id>",
        "name": "AC Repair",
        "description": "Fix your air conditioner",
        "base_price": 499,
        "duration_minutes": 60,
        "icon": "❄️"
    }
    """
    data = request.data

    required = ['dept_id', 'name', 'base_price']
    for field in required:
        if not data.get(field):
            return Response({"error": f"'{field}' is required."}, status=status.HTTP_400_BAD_REQUEST)

    dept_oid = str_to_objectid(data['dept_id'])
    if not dept_oid:
        return Response({"error": "Invalid dept_id."}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the department exists
    dept = db.departments.find_one({"_id": dept_oid})
    if not dept:
        return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

    new_service = {
        "dept_id": dept_oid,
        "name": data['name'].strip(),
        "description": data.get('description', '').strip(),
        "base_price": float(data['base_price']),           # In INR
        "duration_minutes": int(data.get('duration_minutes', 60)),
        "icon": data.get('icon', '🔧'),
        "is_active": True,
        "created_at": datetime.utcnow(),
    }

    result = db.services.insert_one(new_service)
    new_service['_id'] = result.inserted_id

    return Response(serialize_doc(new_service), status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_service(request, service_id):
    """Admin only: Update a service's details."""
    data = request.data

    update_fields = {}
    allowed_fields = ['name', 'description', 'base_price', 'duration_minutes', 'icon', 'is_active']
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if 'dept_id' in data:
        dept_oid = str_to_objectid(data['dept_id'])
        if dept_oid:
            update_fields['dept_id'] = dept_oid

    if not update_fields:
        return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    db.services.update_one(
        {"_id": str_to_objectid(service_id)},
        {"$set": update_fields}
    )

    updated = db.services.find_one({"_id": str_to_objectid(service_id)})
    if not updated:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(serialize_doc(updated))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_service(request, service_id):
    """Admin only: Soft-delete a service (sets is_active=False)."""
    result = db.services.update_one(
        {"_id": str_to_objectid(service_id)},
        {"$set": {"is_active": False}}
    )

    if result.matched_count == 0:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"message": "Service deactivated successfully."})
