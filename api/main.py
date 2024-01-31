from fastapi import FastAPI, Response, status, HTTPException
from pymongo import MongoClient
from .data.models import Part, Category, Location
from .data import validation

tags_metadata = [
    {"name": "parts"},
    {"name": "categories"},
]

app = FastAPI()

# -------------------------- Init database -------------------------- #

with open('connect_info.txt', 'r') as file:
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
    # TODO Ensure that each part belongs to a category
    # TODO Ensure that a part cannot be assigned to a base category.
    return {"message": "parts"}


@app.get("/parts/{serial_number}", tags=["parts"])
async def read_part(serial_number: str = ""):
    return {"message": "parts"}


@app.get("/parts", tags=["parts"])
async def read_parts():
    return []


@app.put("/parts/{serial_number}", tags=["parts"])
async def update_part(serial_number: str = ""):
    # TODO Ensure that each part belongs to a category
    # TODO Ensure that a part cannot be assigned to a base category.
    return {"message": "parts"}


@app.delete("/parts/{serial_number}", tags=["parts"])
async def delete_part(serial_number: str = ""):
    return {"message": "parts"}


# -------------------------- Categories -------------------------- #


@app.post("/categories", tags=["categories"])
async def create_category(category: Category):
    if category.parent_name == category.name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "category parent name can't be same as category name")
    if not validation.is_value_unique(db.categories, {"name": category.name}):
        raise HTTPException(status.HTTP_409_CONFLICT, f"category {category.name} already exists")

    result = db.categories.find_one({"name": category.parent_name})
    if result is None and category.parent_name != "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"parent category with name {category.parent_name} does not exist")

    db.categories.insert_one({
        "name": category.name,
        "parent_name": category.parent_name,
    })
    return {"detail": "created successfully"}


@app.get("/categories", tags=["categories"])
async def read_categories():
    raw_results = db.categories.find({})
    result = []
    for document in raw_results:
        result.append({
            "name": document["name"],
            "parent_name": document["parent_name"]
        })
    return result


@app.get("/categories/{name}", tags=["categories"])
async def read_category(name: str = ""):
    result = db.categories.find_one({"name": name})
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"category with name {name} does not exist")
    return {"name": result["name"], "parent_name": result["parent_name"]}


@app.put("/categories/{name}", tags=["categories"])
async def update_category(response: Response, name: str = ""):
    # TODO Don't update category name if there are parts assigned to it or when child categories reference it
    return {"message": "categories"}


@app.delete("/categories/{name}", tags=["categories"])
async def delete_category(response: Response, name: str = ""):
    # TODO Ensure that a category cannot be removed if there are parts assigned to it.
    # TODO Ensure that a parent category cannot be removed if it has child categories with parts assigned.
    return {"message": "categories"}
