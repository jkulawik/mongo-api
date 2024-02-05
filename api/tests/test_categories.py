from fastapi.testclient import TestClient
from fastapi import status
import pytest
import mongomock

from ..main import app, get_db
from .example_data import fixture_part_1, fixture_deep_copy

client = TestClient(app)

# This segment can be put in override_db() to run each test with a fresh db,
# but using the same instance requires less boilerplate
test_client = mongomock.MongoClient()
test_db = test_client["test_db"]

def override_db():
    try:
        yield test_db
    finally:
        pass


app.dependency_overrides[get_db] = override_db


# TODO fixture probably shouldn't use the API
@pytest.fixture(scope="session", autouse=True)
def init_data_for_delete_and_update():
    # Add base category and subcategories
    response = client.post("/categories", json={"name": "edit_cat1", "parent_name": ""})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "edit_cat2", "parent_name": "edit_cat1"})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "edit_cat3", "parent_name": "edit_cat1"})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "deleteme", "parent_name": "edit_cat1"})
    assert response.status_code == 200

    # Add valid parts for edit_cat2
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["location"]["room"] = "test_room"  # don't hog the example location for parts tests

    test_part["category"] = "edit_cat2"
    test_part["serial_number"] = "zxcasd"
    test_part["name"] = "category test part"
    response = client.post("/parts", json={"part": test_part, "location": test_part["location"]})
    assert response.status_code == 200


# -------------------------- Add / POST -------------------------- #

def test_category_add_invalid():
    # Test FastAPI's type and model validation
    response = client.post("/categories", json={"name": ""})  # missing parameter
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = client.post("/categories", json={"name": 2, "parent_name": ""})  # wrong type
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = client.post("/categories", json={"name": "", "parent_name": ""})  # empty name
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_category_add_self_referencing():
    # Category should not have itself as parent
    response = client.post("/categories", json={"name": "resistors", "parent_name": "resistors"})
    assert response.json() == {"detail": "category parent name can't be same as category name"}
    assert response.status_code == 400


def test_category_add_base_correct():
    # Test regular add of base category
    response = client.post("/categories", json={"name": "abc", "parent_name": ""})
    assert response.json() == {'name': "abc", 'parent_name': ""}
    assert response.status_code == 200


def test_category_add_duplicate():
    # Names should not repeat
    test_category = {"name": "edit_cat1", "parent_name": ""}
    response = client.post("/categories", json=test_category)
    assert response.json() == {"detail": "category edit_cat1 already exists"}
    assert response.status_code == 409


def test_category_add_with_nonexistent_parent():
    # Test adding a category with nonexistent parent
    response = client.post("/categories", json={"name": "xyz", "parent_name": "qwop"})
    assert response.json() == {"detail": "parent category with name qwop does not exist"}
    assert response.status_code == 400


def test_category_add_correct():
    # Test adding a valid base category
    test_category_1 = {"name": "123", "parent_name": ""}
    response = client.post("/categories", json=test_category_1)
    assert response.json() == test_category_1
    assert response.status_code == 200
    # Test adding a valid category with valid parent
    test_category_2 = {"name": "456", "parent_name": "123"}
    response = client.post("/categories", json=test_category_2)
    assert response.json() == test_category_2
    assert response.status_code == 200


# -------------------------- Read / GET -------------------------- #


def test_category_read_nonexistent():
    response = client.get("/categories/doesntexist")
    assert response.status_code == 404


def test_category_read_correct():
    # Test basic get
    response = client.get("/categories/edit_cat2")
    assert response.json() == {"name": "edit_cat2", "parent_name": "edit_cat1"}
    assert response.status_code == 200


def test_category_read_many():
    response = client.get("/categories")
    # NOTE categories from previous tests are still present so no direct comparison here
    assert {"name": "edit_cat2", "parent_name": "edit_cat1"} in response.json()
    assert {"name": "edit_cat1", "parent_name": ""} in response.json()
    assert response.status_code == 200


# -------------------------- Update / PUT -------------------------- #


def test_category_update_nonexistent():
    new_category_data = {"name": "new_name", "parent_name": "edit_cat1"}
    response = client.put("/categories/doesntexist", json=new_category_data)
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_category_rename_with_parts_assigned():
    # Since categories are referenced by ID in the db, we can change their basic data
    new_category_data = {"name": "new_name", "parent_name": "edit_cat1"}
    response = client.put("/categories/edit_cat2", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200
    # Revert the rename to not mess with other tests
    new_category_data["name"] = "edit_cat2"
    response = client.put("/categories/new_name", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200


def test_category_rename_with_child_categories_assigned():
    # Since categories are referenced by ID in the db, we can change their basic data
    new_category_data = {"name": "new_name", "parent_name": ""}
    response = client.put("/categories/edit_cat1", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200
    # Revert the rename to not mess with other tests
    new_category_data["name"] = "edit_cat1"
    response = client.put("/categories/new_name", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200


def test_category_make_base_with_parts_assigned():
    new_category_data = {"name": "edit_cat2", "parent_name": ""}
    response = client.put("/categories/edit_cat2", json=new_category_data)
    assert response.json() == {
        "detail": "can't update/remove category edit_cat2: has parts assigned"
    }


def test_category_update_doublecheck():
    new_category_data = {"name": "new_name2", "parent_name": "edit_cat1"}
    response = client.put("/categories/edit_cat3", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200
    
    # Test if the entry is correctly updated in the db
    response = client.get("/categories/new_name2")
    assert response.json() == {"name": "new_name2", "parent_name": "edit_cat1"}
    assert response.status_code == 200


# -------------------------- Delete -------------------------- #


def test_category_delete_nonexistent():
    response = client.delete("/categories/doesntexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}


def test_category_delete_with_parts_assigned():
    response = client.delete("/categories/edit_cat2")
    assert response.json() == {
        "detail": "can't update/remove category edit_cat2: has parts assigned"
    }
    assert response.status_code == 400


def test_category_delete_with_child_categories_assigned():
    response = client.delete("/categories/edit_cat1")
    assert response.json() == {
        "detail": "can't update/remove category edit_cat1: child categories have parts assigned"
    }
    assert response.status_code == 400


def test_category_delete():
    response = client.delete("/categories/deleteme")
    assert response.json() == {}
    assert response.status_code == 200
    # Test if the entry is correctly removed from the db
    response = client.get("/categories/deleteme")
    assert response.status_code == 404
