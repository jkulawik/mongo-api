from typing import Annotated
from fastapi import FastAPI, status, HTTPException, Query, Depends
from pymongo import MongoClient, ReturnDocument, database

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


def get_part_document(db: database, search_dict: dict):
    result = db.parts.find_one(search_dict)
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"part {search_dict} does not exist"
        )
    return result


# -------------------------- Parts -------------------------- #


@app.post("/parts", tags=["parts"])
def create_part(part: Part, location: Location, db: database = Depends(get_db)):
    category_document = get_category_document(db, {"name": part.category})
    validation.validate_category_accepts_parts(category_document)
    validation.validate_part_unique_serial(db, part)
    validation.validate_part_cuvette_not_taken(db, location)

    # Create a part dict
    part_document = vars(part)
    part_document["location"] = vars(location)

    # Add category ID for the database representation
    part_document["category"] = category_document["_id"]
    db.parts.insert_one(part_document)  # NOTE this implicitly adds _id to part_document

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    part_document["category"] = category_document["name"]
    del part_document["_id"]
    return part_document


@app.get("/parts/{serial_number}", tags=["parts"])
def read_part(serial_number: str, db: database = Depends(get_db)):
    part_document = get_part_document(db, {"serial_number": serial_number})
    category_document = get_category_document(db, {"_id": part_document["category"]})

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    part_document["category"] = category_document["name"]
    del part_document["_id"]
    return part_document


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
        # Replace ObjectIDs with string names for the API and remove the unnecessary ones
        category_document = get_category_document(db, {"_id": document["category"]})
        document["category"] = category_document["name"]
        del document["_id"]
        results.append(document)
    return results


@app.put("/parts/{serial_number}", tags=["parts"])
def update_part(serial_number: str, new_part_data: Part, new_location: Location, db: database = Depends(get_db)):
    new_category_document = get_category_document(db, {"name": new_part_data.category})
    validation.validate_category_accepts_parts(new_category_document)
    validation.validate_part_unique_serial(db, new_part_data)
    validation.validate_part_cuvette_not_taken(db, new_location)

    update_data = vars(new_part_data)
    update_data["location"] = vars(new_location)
    update_data["category"] = new_category_document["_id"]

    updated_part = db.parts.find_one_and_update(
        {"serial_number": serial_number},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    updated_part["category"] = new_category_document["name"]
    del updated_part["_id"]
    return updated_part


@app.delete("/parts/{serial_number}", tags=["parts"])
def delete_part(serial_number: str, db: database = Depends(get_db)):
    return {"detail": "parts"}


# -------------------------- Categories -------------------------- #


@app.post("/categories", tags=["categories"])
def create_category(category: Category, db: database = Depends(get_db)):
    validation.validate_category_unique_name(db, category)
    validation.validate_category_fields(db, category)

    # Get ObjectID from string name for database representation
    parent_id = None
    if category.parent_name != "":
        parent_category = get_category_document(db, {"name": category.parent_name})
        if parent_category is not None:
            parent_id = parent_category["_id"]

    category_document = {
        "name": category.name,
        "parent_id": parent_id,
    }
    db.categories.insert_one(category_document)  # NOTE implicitly adds _id to doc

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    category_document["parent_name"] = category.parent_name
    del category_document["_id"]
    del category_document["parent_id"]
    return category_document


@app.get("/categories", tags=["categories"])
def read_categories(db: database = Depends(get_db)):
    categories = []
    for document in db.categories.find({}):
        # Replace ObjectIDs with string names for the API and remove the unnecessary ones
        if document["parent_id"] is None:
            document["parent_name"] = ""
        else:
            category = get_category_document(db, {"_id": document["parent_id"]})
            document["parent_name"] = category["name"]
        del document["_id"]
        del document["parent_id"]
        categories.append(document)
    return categories


@app.get("/categories/{name}", tags=["categories"])
def read_category(name: str, db: database = Depends(get_db)):
    category_document = get_category_document(db, {"name": name})

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    parent_id = category_document["parent_id"]
    if parent_id is None:
        category_document["parent_name"] = ""
    else:
        parent_category_document = get_category_document(db, {"_id": parent_id})
        category_document["parent_name"] = parent_category_document["name"]

    del category_document["_id"]
    del category_document["parent_id"]
    return category_document


@app.put("/categories/{name}", tags=["categories"])
def update_category(name: str, new_category_data: Category, db: database = Depends(get_db)):
    validation.validate_category_fields(db, new_category_data)
    category_document = get_category_document(db, {"name": name})

    # Find the right category ID for the database representation
    new_parent_id = None
    if new_category_data.parent_name == "":
        validation.validate_category_no_parts(db, category_document)
    else:
        new_parent_document = get_category_document(db, {"name": new_category_data.parent_name})
        new_parent_id = new_parent_document["_id"]

    updated_category = db.categories.find_one_and_update(
        {"_id": category_document["_id"]},
        {"$set": {"name": new_category_data.name, "parent_id": new_parent_id}},
        return_document=ReturnDocument.AFTER
    )

    # Replace ObjectIDs with string names for the API and remove the unnecessary ones
    updated_category["parent_name"] = new_category_data.parent_name
    del updated_category["_id"]
    del updated_category["parent_id"]
    return updated_category


@app.delete("/categories/{name}", tags=["categories"])
def delete_category(name: str, db: database = Depends(get_db)):
    category = get_category_document(db, {"name": name})
    validation.validate_category_no_parts(db, category)
    validation.validate_category_children_have_no_parts(db, category)

    result = db.categories.find_one_and_delete({"_id": category["_id"]})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    return {}
