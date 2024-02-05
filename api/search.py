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
    matches = []
    t = params["t"]
    
    # Full text search with db indexing would probably be better
    direct_text_filter = {
        "$or": [
            {"serial_number":{"$regex": t}},
            {"name":{"$regex": t}},
            {"description":{"$regex": t}},
            {"location.room":{"$regex": t}},
        ]
    }
    matches = list(db.parts.find(direct_text_filter))

    print("all ref'd cats", list(db.parts.find({}, {"_id": 0, "category": 1})))

    ids_of_matching_categories = []
    for doc in db.categories.find({"name": {"$regex": t}}, {"_id": 1}):
        ids_of_matching_categories.append(doc["_id"])
    # a = list(db.categories.find({"name": {"$regex": t}}, {"_id": 1}))
    # print(a)
    # FIXME this isn't matching any results
    cat_matches = list(db.parts.find({"_id": {"$in": ids_of_matching_categories}}))
    print(ids_of_matching_categories)
    print(cat_matches)
    matches += cat_matches

    return matches
