"""
Technician views for SevaConnect.

Technicians are users who provide services.
After registering with role='technician', they set up their profile here.
Customers can browse technicians by service or city.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, serialize_list, str_to_objectid
from common.permissions import IsTechnician, IsAdmin


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTechnician])
def get_my_profile(request):
    """
    Technician: Get your own profile.
    Returns the technician document merged with user info.
    """
    user = request.user
    tech = db.technicians.find_one({"user_id": str_to_objectid(user.id)})

    if not tech:
        return Response({"error": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        **serialize_doc(tech),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsTechnician])
def update_my_profile(request):
    """
    Technician: Update your own profile.

    Updatable fields:
    {
        "bio": "10 years of experience in electrical repairs",
        "city": "Mumbai",
        "pincode": "400001",
        "experience_years": 10,
        "services": ["<service_id_1>", "<service_id_2>"]
    }
    """
    user = request.user
    data = request.data

    update_fields = {}
    allowed_fields = ['bio', 'city', 'pincode', 'experience_years']
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    # Services list: convert string IDs to ObjectIds
    if 'services' in data and isinstance(data['services'], list):
        service_oids = []
        for sid in data['services']:
            oid = str_to_objectid(sid)
            if oid:
                service_oids.append(oid)
        update_fields['services'] = service_oids

    if not update_fields:
        return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    db.technicians.update_one(
        {"user_id": str_to_objectid(user.id)},
        {"$set": update_fields}
    )

    updated = db.technicians.find_one({"user_id": str_to_objectid(user.id)})
    return Response({
        **serialize_doc(updated),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_technicians(request):
    """
    Public: List all verified technicians.

    Query params:
        ?city=Mumbai         - filter by city
        ?service_id=<id>     - filter by service they offer
        ?pincode=400001      - filter by pincode
    """
    query = {"is_verified": True}

    city = request.query_params.get('city', '').strip()
    if city:
        query['city'] = {"$regex": city, "$options": "i"}

    pincode = request.query_params.get('pincode', '').strip()
    if pincode:
        query['pincode'] = pincode

    service_id = request.query_params.get('service_id', '').strip()
    if service_id:
        service_oid = str_to_objectid(service_id)
        if service_oid:
            query['services'] = service_oid

    technicians = list(db.technicians.find(query).sort("ratings_avg", -1))

    # Enrich each technician with their user info
    result = []
    for tech in technicians:
        user_data = db.users.find_one({"_id": tech.get("user_id")})
        if user_data:
            tech_data = serialize_doc(tech)
            tech_data['name'] = user_data.get('name', '')
            tech_data['phone'] = user_data.get('phone', '')
            result.append(tech_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_technician(request, tech_id):
    """
    Public: Get a single technician's public profile.
    """
    tech = db.technicians.find_one({"_id": str_to_objectid(tech_id)})
    if not tech:
        return Response({"error": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

    user_data = db.users.find_one({"_id": tech.get("user_id")})
    tech_data = serialize_doc(tech)
    if user_data:
        tech_data['name'] = user_data.get('name', '')
        tech_data['phone'] = user_data.get('phone', '')

    return Response(tech_data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def verify_technician(request, tech_id):
    """
    Admin only: Verify or unverify a technician.
    Body: {"is_verified": true}
    """
    is_verified = request.data.get('is_verified', True)
    result = db.technicians.update_one(
        {"_id": str_to_objectid(tech_id)},
        {"$set": {"is_verified": bool(is_verified)}}
    )

    if result.matched_count == 0:
        return Response({"error": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"message": f"Technician {'verified' if is_verified else 'unverified'} successfully."})
