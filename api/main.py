from typing import Annotated
from fastapi import FastAPI, status, HTTPException, Query, Depends
from pymongo import MongoClient, ReturnDocument, CursorType, database
from .data.models import Part, Category, Location
from .data import validation

tags_metadata = [
    {"name": "parts"},
    {"name": "categories"},
]

app = FastAPI()

# -------------------------- Init database -------------------------- #

with open('connect_info.txt', 'r', encoding="utf-8") as file:
    connection_string = file.readline()
    db_name = file.readline()

client = MongoClient(connection_string)
_database = client[db_name]

# collections = _database.list_collection_names()
# if "parts" in collections:
#     _database.parts.delete_many({})  # delete all documents
# else:
#     _database.create_collection("parts")
# if "categories" in collections:
#     _database.categories.delete_many({})
# else:
#     _database.create_collection("categories")


# Dependency - note that this is ran each time a function with Depends is called
def get_db():
    try:
        yield _database
    finally:
        pass


# -------------------------- Utilities -------------------------- #


def get_dicts_from_cursor(cursor: CursorType):
    result = []
    for document in cursor:
        del document["_id"]
        result.append(document)
    return result


# -------------------------- Parts -------------------------- #


@app.post("/parts", tags=["parts"])
def create_part(part: Part, location: Location, db: database = Depends(get_db)):
    validation.validate_part(db, part.category)
    doc = vars(part)
    doc["location"] = vars(location)
    db.parts.insert_one(doc)
    del doc["_id"]
    return doc


@app.get("/parts/{serial_number}", tags=["parts"])
def read_part(serial_number: str, db: database = Depends(get_db)):
    result = db.parts.find_one({"serial_number": serial_number})
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"part with serial_number {serial_number} does not exist"
        )
    del result["_id"]
    return result


@app.get("/parts", tags=["parts"])
def read_parts(q: Annotated[str | None, Query(max_length=50)] = None, db: database = Depends(get_db)):
    if q is None:
        cursor = db.parts.find({})
        return get_dicts_from_cursor(cursor)
    # TODO Search for parts based on all mandatory ﬁelds

    cursor = db.parts.find({})
    return get_dicts_from_cursor(cursor)


@app.put("/parts/{serial_number}", tags=["parts"])
def update_part(serial_number: str, new_part_data: Part, new_location: Location, db: database = Depends(get_db)):
    validation.validate_part(db, new_part_data.category)
    return {"detail": "parts"}


@app.delete("/parts/{serial_number}", tags=["parts"])
def delete_part(serial_number: str, db: database = Depends(get_db)):
    return {"detail": "parts"}


# -------------------------- Categories -------------------------- #


@app.post("/categories", tags=["categories"])
def create_category(category: Category, db: database = Depends(get_db)):
    validation.validate_category(db, category)
    if not validation.is_value_unique(db.categories, {"name": category.name}):
        raise HTTPException(status.HTTP_409_CONFLICT, f"category {category.name} already exists")
    doc = {
        "name": category.name,
        "parent_name": category.parent_name,
        }
    db.categories.insert_one(doc)
    del doc["_id"]
    return doc


@app.get("/categories", tags=["categories"])
def read_categories(db: database = Depends(get_db)):
    cursor = db.categories.find({})
    return get_dicts_from_cursor(cursor)


@app.get("/categories/{name}", tags=["categories"])
def read_category(name: str, db: database = Depends(get_db)):
    result = db.categories.find_one({"name": name})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    del result["_id"]
    return result


@app.put("/categories/{name}", tags=["categories"])
def update_category(name: str, new_category: Category, db: database = Depends(get_db)):
    if new_category.name != name:
        validation.validate_category(db, new_category)
        validation.validate_category_editable(db, name)
    # Parent can be updated even when parts and child categories exist
    part = db.parts.find_one({"category": name})
    if new_category.parent_name == "":
        if part is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"can't make category {name} a base category: has parts assigned"
            )
    result = db.categories.find_one_and_update(
        {"name": name},
        {"$set": {"name": new_category.name, "parent_name": new_category.parent_name}},
        return_document=ReturnDocument.AFTER)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    del result["_id"]
    return result


@app.delete("/categories/{name}", tags=["categories"])
def delete_category(name: str, db: database = Depends(get_db)):
    validation.validate_category_editable(db, name)

    result = db.categories.find_one_and_delete({"name": name})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    return {}
