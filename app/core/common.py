from typing import Any
from bson import ObjectId


def stringify_object_ids(obj: Any) -> Any:
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [stringify_object_ids(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: stringify_object_ids(value) for key, value in obj.items()}
    return obj
