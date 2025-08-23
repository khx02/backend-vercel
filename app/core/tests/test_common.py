from bson import ObjectId

from app.core.common import stringify_object_ids


def test_stringify_object_ids_success():
    input_data = [
        {"_id": ObjectId(), "name": "Test", "member_ids": [ObjectId()]},
        {"_id": ObjectId(), "name": "Another Test", "member_ids": []},
    ]
    expected_output = [
        {
            "_id": str(item["_id"]),
            "name": item["name"],
            "member_ids": [str(mid) for mid in item["member_ids"]],
        }
        for item in input_data
    ]
    assert stringify_object_ids(input_data) == expected_output
