"""
MongoDB connection for SevaConnect.
"""

from pymongo import MongoClient
from django.conf import settings


_client = None
db = None


def get_db():
    """Create MongoDB connection and check that it is reachable."""
    global _client, db

    if _client is None:
        mongo_uri = settings.MONGO_URI

        _client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000
        )

        # Actually test the MongoDB connection
        _client.admin.command("ping")

        # Get database name from MongoDB URI
        db_name = mongo_uri.split('/')[-1].split('?')[0]

        if not db_name:
            db_name = "sevaconnect"

        db = _client[db_name]

        print("✅ MongoDB ping successful")

    return db


try:
    db = get_db()
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None