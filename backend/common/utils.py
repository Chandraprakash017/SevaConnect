"""
Common utility functions used across SevaConnect apps.
"""

from bson import ObjectId
from datetime import datetime


def str_to_objectid(id_string):
    """
    Convert a string ID to a MongoDB ObjectId.
    Returns None if the string is not a valid ObjectId.
    """
    try:
        return ObjectId(id_string)
    except Exception:
        return None


def serialize_doc(doc):
    """
    Convert a MongoDB document to a JSON-serializable dictionary.
    MongoDB stores _id as ObjectId, which JSON can't serialize directly.
    This converts _id to a string and handles nested ObjectIds.
    """
    if doc is None:
        return None

    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(item) if isinstance(item, dict) else
                str(item) if isinstance(item, ObjectId) else item
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value

    return result


def serialize_list(docs):
    """Serialize a list of MongoDB documents."""
    return [serialize_doc(doc) for doc in docs]


def get_current_time():
    """Get current datetime. Used for created_at and updated_at fields."""
    return datetime.utcnow()
