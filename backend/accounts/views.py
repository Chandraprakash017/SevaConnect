"""
Accounts views for SevaConnect.

Handles user registration, login, and token refresh.
Users are stored in the MongoDB 'users' collection.
"""

import bcrypt
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from common.db import db
from common.utils import serialize_doc


def generate_tokens_for_user(user_id, role):
    """
    Generate JWT access and refresh tokens for a user.
    We store the user_id and role inside the token payload
    so we can read them without a database lookup on every request.
    """
    # Create a refresh token with custom claims
    refresh = RefreshToken()
    refresh['user_id'] = str(user_id)
    refresh['role'] = role

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user (customer or technician).
    
    Expected request body:
    {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "password": "securepassword",
        "phone": "9876543210",
        "role": "customer"   # or "technician"
    }
    """
    data = request.data

    # Validate required fields
    required_fields = ['name', 'email', 'password', 'phone', 'role']
    for field in required_fields:
        if not data.get(field):
            return Response(
                {"error": f"'{field}' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Only customers and technicians can self-register
    # Admins are created manually
    if data['role'] not in ('customer', 'technician'):
        return Response(
            {"error": "Role must be 'customer' or 'technician'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    email = data['email'].lower().strip()

    # Check if email is already registered
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return Response(
            {"error": "An account with this email already exists."},
            status=status.HTTP_409_CONFLICT
        )

    # Hash the password using bcrypt before storing
    password_hash = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Build the user document to save in MongoDB
    new_user = {
        "name": data['name'].strip(),
        "email": email,
        "password_hash": password_hash,
        "phone": data['phone'].strip(),
        "role": data['role'],
        "is_active": True,
        "created_at": datetime.utcnow(),
    }

    # Save user to MongoDB
    result = db.users.insert_one(new_user)
    user_id = result.inserted_id

    # If registering as a technician, create a basic technician profile too
    if data['role'] == 'technician':
        db.technicians.insert_one({
            "user_id": user_id,
            "services": [],        # Will be filled in profile setup
            "city": "",
            "pincode": "",
            "bio": "",
            "experience_years": 0,
            "is_verified": False,  # Admin verifies technicians
            "ratings_avg": 0.0,
            "total_jobs": 0,
            "created_at": datetime.utcnow(),
        })

    # Generate JWT tokens immediately after registration
    tokens = generate_tokens_for_user(user_id, data['role'])

    return Response({
        "message": "Account created successfully.",
        "user": {
            "id": str(user_id),
            "name": new_user['name'],
            "email": new_user['email'],
            "role": new_user['role'],
        },
        "tokens": tokens
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with email and password. Returns JWT tokens.
    
    Expected request body:
    {
        "email": "rahul@example.com",
        "password": "securepassword"
    }
    """
    data = request.data
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find the user in MongoDB
    user = db.users.find_one({"email": email})

    if user is None:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if account is active
    if not user.get('is_active', True):
        return Response(
            {"error": "Your account has been disabled. Please contact support."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Verify the password against the stored hash
    password_matches = bcrypt.checkpw(
        password.encode('utf-8'),
        user['password_hash'].encode('utf-8')
    )

    if not password_matches:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate fresh JWT tokens
    tokens = generate_tokens_for_user(user['_id'], user['role'])

    return Response({
        "message": "Login successful.",
        "user": {
            "id": str(user['_id']),
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "phone": user.get('phone', ''),
        },
        "tokens": tokens
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    Get the currently logged-in user's profile.
    The user is attached to request.user by our custom JWT authentication.
    """
    user = request.user
    user_data = db.users.find_one({"_id": __import__('bson').ObjectId(user.id)})

    if not user_data:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Return user info without the password hash
    return Response({
        "id": str(user_data['_id']),
        "name": user_data['name'],
        "email": user_data['email'],
        "phone": user_data.get('phone', ''),
        "role": user_data['role'],
        "created_at": user_data['created_at'].isoformat() if user_data.get('created_at') else None,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update name and phone number of the logged-in user."""
    user = request.user
    data = request.data

    update_fields = {}
    if data.get('name'):
        update_fields['name'] = data['name'].strip()
    if data.get('phone'):
        update_fields['phone'] = data['phone'].strip()

    if not update_fields:
        return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    db.users.update_one(
        {"_id": __import__('bson').ObjectId(user.id)},
        {"$set": update_fields}
    )

    return Response({"message": "Profile updated successfully."})
