from pymongo import collection, database
from fastapi import HTTPException, status
from .models import Category  # NOTE this gets marked by pylint as an error but it's a false positive


def is_value_unique(_collection: collection, _filter: dict) -> bool:
    return _collection.count_documents(_filter, limit=1) == 0


def validate_category(db: database, category: Category):
    if category.parent_name == category.name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "category parent name can't be same as category name")

    result = db.categories.find_one({"name": category.parent_name})
    if result is None and category.parent_name != "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"parent category with name {category.parent_name} does not exist")


def validate_category_editable(db: database, name: str):
    child_category = db.categories.find_one({"parent_name": name})
    part = db.parts.find_one({"category": name})
    if part is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"can't update/remove category {name}: has parts assigned")
    if child_category is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"can't update/remove category {name}: referenced by child categories")

