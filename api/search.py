from typing import Annotated
from fastapi import Query

from .data.models import DEFAULT_MAX_LEN

def search_params(
    t: Annotated[str | None, Query(title="Text search", max_length=DEFAULT_MAX_LEN,)] = None,
    ):
    if t is None:
        return None
    return {"t": t}


def search_parts(db, params: dict):
    # TODO add other parameters to search
    t = params["t"]

    matching_category_ids = []
    for doc in db.categories.find({"name": {"$regex": t}}, {"_id": 1}):
        matching_category_ids.append(doc["_id"])

    search_filter = {
        "$or": [
            {"serial_number":{"$regex": t}},
            {"name":{"$regex": t}},
            {"description":{"$regex": t}},
            {"location.room":{"$regex": t}},
            {"category": {"$in": matching_category_ids}},
        ]
    }
    return list(db.parts.find(search_filter))
