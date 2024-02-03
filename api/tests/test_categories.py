from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..main import app
from .example_data import test_location_template, test_part_template
client = TestClient(app)


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

    # Add a valid part for edit_cat2
    test_part = test_part_template.copy()
    test_part["category"] = "edit_cat2"
    response = client.post("/parts", json={"part": test_part, "location": test_location_template})
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
    assert {"name": "test_category2", "parent_name": ""} in response.json()
    assert {"name": "test_category3", "parent_name": ""} in response.json()
    assert response.status_code == 200


# -------------------------- Update / PUT -------------------------- #


def test_category_update_nonexistent():
    new_category_data = {"name": "new_name", "parent_name": "edit_cat1"}
    response = client.put("/categories/doesntexist", json=new_category_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "category with name doesntexist does not exist"}


def test_category_rename_with_parts_assigned():
    new_category_data = {"name": "new_name", "parent_name": ""}
    response = client.put("/categories/edit_cat2", json=new_category_data)
    assert response.json() == {
        "detail": "can't update/remove category edit_cat2: has parts assigned"
    }
    assert response.status_code == 400


def test_category_rename_with_child_categories_assigned():
    new_category_data = {"name": "new_name", "parent_name": ""}
    response = client.put("/categories/edit_cat1", json=new_category_data)
    assert response.json() == {
        "detail": "can't update/remove category edit_cat1: child categories have parts assigned"
    }
    assert response.status_code == 400


def test_category_make_base_with_parts_assigned():
    new_category_data = {"name": "edit_cat2", "parent_name": ""}
    response = client.put("/categories/edit_cat2", json=new_category_data)
    assert response.json() == {
        "detail": "can't make category edit_cat2 a base category: has parts assigned"
    }


def test_category_update():
    new_category_data = {"name": "new_name", "parent_name": "edit_cat1"}
    response = client.put("/categories/edit_cat3", json=new_category_data)
    assert response.json() == new_category_data
    assert response.status_code == 200
    # Test if the entry is correctly updated in the db
    response = client.get("/categories/new_name")
    assert response.json() == {"name": "new_name", "parent_name": "edit_cat1"}
    assert response.status_code == 200


# -------------------------- Delete -------------------------- #


def test_category_delete_nonexistent():
    response = client.delete("/categories/doesntexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "category with name doesntexist does not exist"}


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
