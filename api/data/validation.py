from pymongo import collection, database
from fastapi import HTTPException, status

# NOTE: This gets marked by pylint as an error but it's a false positive
from .models import Category, Location, Part


# -------------------------- Validation of new data -------------------------- #


def validate_category_unique_name(db: database, category: Category):
    duplicate = db.categories.find_one({"name": category.name})
    if duplicate is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"category {category.name} already exists")


def validate_part_unique_serial(db: database, part: Part):
    duplicate = db.parts.find_one({"serial_number": part.serial_number})
    if duplicate is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"serial {part.serial_number} already exists")


def validate_category_fields(db: database, category: Category):
    if category.parent_name == category.name:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "category parent name can't be same as category name"
        )

    parent_category_document = db.categories.find_one({"name": category.parent_name})
    if parent_category_document is None and category.parent_name != "":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"parent category with name {category.parent_name} does not exist"
        )



# -------------------------- Validation of existing documents -------------------------- #


def validate_category_no_parts(db: database, category_document: dict):
    # Ensure that a category cannot be edited/removed if there are parts assigned to it.
    part = db.parts.find_one({"category": category_document["_id"]})
    if part is not None:
        category_name = category_document["name"]
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"can't update/remove category {category_name}: has parts assigned"
        )


def validate_category_children_have_no_parts(db: database, category_document: dict):
    # Ensure that a parent category can't be removed if it has child categories with parts assigned.
    cursor = db.categories.find({"parent_id": category_document["_id"]})
    for child_document in cursor:
        child_category_id = child_document["_id"]
        child_part = db.parts.find_one({"category": child_category_id})
        if child_part is not None:
            name = category_document["name"]
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"can't update/remove category {name}: child categories have parts assigned"
            )


def validate_category_accepts_parts(category_document: dict):
    # Ensure that a part cannot be in a base category.
    if category_document["parent_id"] is None:
        name = category_document["name"]
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"part can't be assigned to a base category ({name})"
        )


def validate_part_cuvette_not_taken(db: database, location: Location):
    part_in_location = db.parts.find_one({"location": location})
    if part_in_location is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"another part is already at location: {location}"
        )
