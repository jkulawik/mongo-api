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

def get_category_document(db: database, search_dict: dict):
    result = db.categories.find_one(search_dict)
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"part category {search_dict} does not exist"
        )
    return result


# -------------------------- Parts -------------------------- #


@app.post("/parts", tags=["parts"])
def create_part(part: Part, location: Location, db: database = Depends(get_db)):
    # NOTE PyMongo implicitly replaces part.category with an ObjectID here. Thanks, PyMongo!
    category = get_category_document(db, {"name": part.category})
    validation.validate_category_accepts_parts(category)
    doc = vars(part)
    doc["location"] = vars(location)
    doc["category"] = category["_id"]  # category is an ID in the db
    db.parts.insert_one(doc)
    doc["category"] = category["name"]  # but we return the name instead of an ID
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
    category = get_category_document(db, {"_id": result["category"]})
    result["category"] = category["name"]
    del result["_id"]
    return result


@app.get("/parts", tags=["parts"])
def read_parts(q: Annotated[str | None, Query(max_length=50)] = None, db: database = Depends(get_db)):
    if q is None:
        cursor = db.parts.find({})
    else:
        # TODO Search for parts based on all mandatory ﬁelds
        pass

    cursor = db.parts.find({})
    results = []
    for document in cursor:
        del document["_id"]
        results.append(document)
    return results


@app.put("/parts/{serial_number}", tags=["parts"])
def update_part(serial_number: str, new_part_data: Part, new_location: Location, db: database = Depends(get_db)):
    validation.validate_category_accepts_parts(new_part_data.category)
    return {"detail": "parts"}


@app.delete("/parts/{serial_number}", tags=["parts"])
def delete_part(serial_number: str, db: database = Depends(get_db)):
    return {"detail": "parts"}


# -------------------------- Categories -------------------------- #


@app.post("/categories", tags=["categories"])
def create_category(category: Category, db: database = Depends(get_db)):
    validation.validate_category_unique_name(db, category)
    validation.validate_category_fields(db, category)
    parent_id = None
    if category.parent_name != "":
        parent_category = get_category_document(db, {"name": category.parent_name})
        if parent_category is not None:
            parent_id = parent_category["_id"]
    doc = {
        "name": category.name,
        "parent_name": parent_id,
    }
    db.categories.insert_one(doc)
    doc["parent_name"] = category.parent_name
    del doc["_id"]
    return doc


@app.get("/categories", tags=["categories"])
def read_categories(db: database = Depends(get_db)):
    cursor = db.categories.find({})
    result = []
    for document in cursor:
        del document["_id"]
        print(document)
        if document["parent_name"] is None:
            document["parent_name"] = ""
        else:
            category = get_category_document(db, {"_id": document["parent_name"]})
            document["parent_name"] = category["name"]
        print(document)
        result.append(document)
    return result


@app.get("/categories/{name}", tags=["categories"])
def read_category(name: str, db: database = Depends(get_db)):
    result = db.categories.find_one({"name": name})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    if result["parent_name"] is None:
        result["parent_name"] = ""
    del result["_id"]
    return result


@app.put("/categories/{name}", tags=["categories"])
def update_category(name: str, new_category: Category, db: database = Depends(get_db)):
    category = get_category_document(db, {"name": name})
    validation.validate_category_fields(db, new_category)
    if new_category.parent_name == "":
        validation.validate_category_no_parts(db, category)
    result = db.categories.find_one_and_update(
        {"_id": category["_id"]},
        {"$set": {"name": new_category.name, "parent_name": new_category.parent_name}},
        return_document=ReturnDocument.AFTER)
    del result["_id"]
    return result


@app.delete("/categories/{name}", tags=["categories"])
def delete_category(name: str, db: database = Depends(get_db)):
    category = get_category_document(db, {"name": name})
    validation.validate_category_no_parts(db, category)
    validation.validate_category_children_no_parts(db, name)

    # TODO replace name with ID
    result = db.categories.find_one_and_delete({"_id": category["_id"]})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    return {}
