"""
Custom JWT authentication backend for SevaConnect.

Django Simple JWT expects a Django User model by default.
Since we use MongoDB (no Django ORM), we need to create a lightweight
"user object" that Simple JWT can attach to request.user.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from common.db import db
from common.utils import str_to_objectid


class MongoUser:
    """
    A lightweight user object built from MongoDB data.
    Django REST Framework needs request.user to have certain attributes.
    This class provides those without needing a Django ORM model.
    """

    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data.get('email', '')
        self.name = user_data.get('name', '')
        self.role = user_data.get('role', 'customer')
        self.phone = user_data.get('phone', '')
        self.is_active = user_data.get('is_active', True)
        self.is_authenticated = True  # Required by DRF

    def __str__(self):
        return self.email


class MongoJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that looks up users from MongoDB
    instead of Django's built-in user database.
    """

    def get_user(self, validated_token):
        """
        Called by DRF after token is validated.
        We look up the user from MongoDB using the user_id from the token.
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise InvalidToken("Token has no user_id claim")

            # Look up the user in MongoDB
            user_data = db.users.find_one({"_id": str_to_objectid(user_id)})

            if user_data is None:
                raise AuthenticationFailed("User not found")

            if not user_data.get('is_active', True):
                raise AuthenticationFailed("User account is disabled")

            # Return our lightweight MongoUser object
            return MongoUser(user_data)

        except Exception as e:
            raise InvalidToken(f"Authentication failed: {str(e)}")
