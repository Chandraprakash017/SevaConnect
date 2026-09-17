"""
MongoDB connection for SevaConnect.

We use pymongo directly instead of an ORM adapter.
This keeps the code simple and easy to understand.

Usage in any view:
    from common.db import db
    user = db.users.find_one({"email": email})
"""

import os
from pymongo import MongoClient
from django.conf import settings


# Create a single MongoDB client that is reused across all requests
# MongoClient is thread-safe so this is the recommended pattern
_client = None
db = None


def get_db():
    """Get the MongoDB database instance. Creates connection if not already connected."""
    global _client, db

    if _client is None:
        mongo_uri = settings.MONGO_URI
        _client = MongoClient(mongo_uri)

        # Extract database name from URI, or use 'sevaconnect' as default
        db_name = mongo_uri.split('/')[-1].split('?')[0] or 'sevaconnect'
        db = _client[db_name]

    return db


# Initialize the db connection when this module is imported
try:
    db = get_db()
    print("✅ Connected to MongoDB successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None
