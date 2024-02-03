from pymongo import collection, database
from fastapi import HTTPException, status
from .models import Category  # This gets marked by pylint as an error but it's a false positive


def is_value_unique(_collection: collection, _filter: dict) -> bool:
    return _collection.count_documents(_filter, limit=1) == 0


def validate_category(db: database, category: Category):
    if category.parent_name == category.name:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "category parent name can't be same as category name"
        )

    result = db.categories.find_one({"name": category.parent_name})
    if result is None and category.parent_name != "":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"parent category with name {category.parent_name} does not exist"
        )


def validate_category_editable(db: database, name: str):
    # Ensure that a category cannot be edited/removed if there are parts assigned to it.
    part = db.parts.find_one({"category": name})
    if part is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"can't update/remove category {name}: has parts assigned"
        )
    # Ensure that a parent category can't be removed if it has child categories with parts assigned.
    cursor = db.categories.find({"parent_name": name})
    for document in cursor:
        child_category_name = document["name"]
        child_part = db.parts.find_one({"category": child_category_name})
        if child_part is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"can't update/remove category {name}: child categories have parts assigned"
            )


# -------------------------- Parts -------------------------- #


def validate_part(db: database, category_name: str):
    result = db.categories.find_one({"name": category_name})
    if result is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"part category {category_name} does not exist"
            )
    if result["parent_name"] == "":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"part can't be assigned to a base category ({category_name})"
            )
