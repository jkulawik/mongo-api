from fastapi import FastAPI, Response, status, HTTPException
from pymongo import MongoClient, ReturnDocument
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
db = client[db_name]

collections = db.list_collection_names()
if "parts" in collections:
    db.parts.delete_many({})  # delete all documents
else:
    db.create_collection("parts")
if "categories" in collections:
    db.categories.delete_many({})
else:
    db.create_collection("categories")

# -------------------------- Parts -------------------------- #
# TODO Search for parts based on all mandatory ﬁelds


@app.post("/parts", tags=["parts"])
async def create_part(part: Part, location: Location):
    result = db.categories.find_one({"name": part.category})
    if result is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"part category {part.category} does not exist"
            )
    if result["parent_name"] == "":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"part can't be assigned to a base category ({part.category})"
            )
    doc = vars(part)
    db.parts.insert_one(doc)
    # NOTE pymongo inserts "_id": ObjectID() into the dict. It crashes FastAPI and pytest because
    # it's not serialisable, and since it's not needed by the end user we just remove it
    del doc["_id"]
    return doc


@app.get("/parts/{serial_number}", tags=["parts"])
async def read_part(serial_number: str = ""):
    return {"detail": "parts"}


@app.get("/parts", tags=["parts"])
async def read_parts():
    return []


@app.put("/parts/{serial_number}", tags=["parts"])
async def update_part(serial_number: str = ""):
    # TODO Ensure that each part belongs to a category
    # TODO Ensure that a part cannot be assigned to a base category.
    return {"detail": "parts"}


@app.delete("/parts/{serial_number}", tags=["parts"])
async def delete_part(serial_number: str = ""):
    return {"detail": "parts"}


# -------------------------- Categories -------------------------- #


@app.post("/categories", tags=["categories"])
async def create_category(category: Category):
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
async def read_categories():
    cursor = db.categories.find({})
    result = []
    for document in cursor:
        del document["_id"]
        result.append(document)
    return result


@app.get("/categories/{name}", tags=["categories"])
async def read_category(name: str = ""):
    result = db.categories.find_one({"name": name})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    del result["_id"]
    return result


@app.put("/categories/{name}", tags=["categories"])
async def update_category(name: str, new_category: Category):
    # Test if category exists, like in read_category
    category = db.categories.find_one({"name": name})
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")

    if new_category.name != name:
        validation.validate_category(db, new_category)
        validation.validate_category_editable(db, name)
    # Parent can be updated even when parts and child categories exist
    part = db.parts.find_one({"category": name})
    if new_category.parent_name == "":
        if part is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"can't make category {name} a base category: has parts assigned")

    result = db.categories.find_one_and_update(
        {"name": name},
        {"$set": {"name": new_category.name, "parent_name": new_category.parent_name}},
        return_document=ReturnDocument.AFTER)
    del result["_id"]
    return result


@app.delete("/categories/{name}", tags=["categories"])
async def delete_category(name: str = ""):
    # TODO Ensure that a category cannot be removed if there are parts assigned to it.
    # TODO Ensure that a parent category cannot be removed if it has child categories with parts assigned.
    return {"message": "categories"}
