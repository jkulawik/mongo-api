from fastapi.testclient import TestClient
from fastapi import status
from ..main import app
from .example_data import test_location_template, test_part_template


client = TestClient(app)

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
    # Test self-referencing category
    response = client.post("/categories", json={"name": "resistors", "parent_name": "resistors"})
    assert response.json() == {"detail": "category parent name can't be same as category name"}
    assert response.status_code == 400


def test_category_add_base_correct():
    # Test regular add of base category
    response = client.post("/categories", json={"name": "abc", "parent_name": ""})
    assert response.json() == {'name': "abc", 'parent_name': ""}
    assert response.status_code == 200


def test_category_add_duplicate():
    # Test trying to add duplicates
    test_category = {"name": "def", "parent_name": ""}
    response = client.post("/categories", json=test_category)
    assert response.json() == test_category
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "def", "parent_name": ""})
    assert response.json() == {"detail": "category def already exists"}
    assert response.status_code == 409


def test_category_add_with_nonexistent_parent():
    # Test adding a category with nonexistent parent
    response = client.post("/categories", json={"name": "xyz", "parent_name": "qwop"})
    assert response.json() == {"detail": "parent category with name qwop does not exist"}
    assert response.status_code == 400


def test_category_add_correct():
    # Add a valid parent
    test_category_1 = {"name": "123", "parent_name": ""}
    response = client.post("/categories", json=test_category_1)
    assert response.json() == test_category_1
    assert response.status_code == 200
    # Test add a category with valid parent
    test_category_2 = {"name": "456", "parent_name": "123"}
    response = client.post("/categories", json=test_category_2)
    assert response.json() == test_category_2
    assert response.status_code == 200


# -------------------------- Read / GET -------------------------- #


def test_category_read_nonexistent():
    response = client.get("/categories/doesntexist")
    assert response.status_code == 404


def test_category_read_correct():
    # Create an entry to get
    client.post("/categories", json={"name": "test_category", "parent_name": ""})
    # Test basic get
    response = client.get("/categories/test_category")
    assert response.json() == {"name": "test_category", "parent_name": ""}
    assert response.status_code == 200


def test_category_read_many():
    # Insert test data
    response = client.post("/categories", json={"name": "test_category2", "parent_name": ""})
    assert response.json() == {"name": "test_category2", "parent_name": ""}
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "test_category3", "parent_name": ""})
    assert response.json() == {"name": "test_category3", "parent_name": ""}
    assert response.status_code == 200
    # Test the all categories endpoint
    response = client.get("/categories")
    # NOTE categories from previous tests are still present so no direct comparison here
    assert {"name": "test_category", "parent_name": ""} in response.json()
    assert {"name": "test_category2", "parent_name": ""} in response.json()
    assert response.status_code == 200


# -------------------------- Update / PUT -------------------------- #
# TODO test category update

def test_category_rename_with_parts_assigned():
    # TODO create a set of available data on test start

    new_category_data = {"name": "new_name", "parent_name": ""}
    response = client.put("/categories/edit_me", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200


def test_category_change_parent_to_self():
    assert False


def test_category_change_parent_to_nonexistent():
    assert False


def test_category_update():
    assert False


# -------------------------- Delete -------------------------- #
# TODO test category delete

def test_category_delete():
    pass
