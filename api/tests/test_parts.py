from fastapi.testclient import TestClient
import pytest
import mongomock
from ..main import app, get_db
from .example_data import test_location_template, test_part_template

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

@pytest.fixture(scope="session", autouse=True)
def init_data_for_parts_testing():
    # Add base category and subcategory
    response = client.post("/categories", json={"name": "base_parts", "parent_name": ""})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "test_parts", "parent_name": "base_parts"})
    assert response.status_code == 200


# -------------------------- Add / POST -------------------------- #


def test_part_add_to_nonexistent_category():
    test_part = test_part_template.copy()
    test_part["category"] = "doesntexist"
    # Test trying to add nonexistent category
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_location_template}
    )
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 400


def test_part_add_to_base_category():
    # Test trying to add to base category
    response = client.post(
        "/parts",
        json={"part": test_part_template, "location": test_location_template}
    )
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_add_correct():
    # Test trying to add to a valid part
    test_part = test_part_template.copy()
    test_part["category"] = "test_parts"
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_location_template}
    )
    # Location is not a part of the Part model: like in the API, it has to be added to JSON manually
    test_part["location"] = test_location_template
    assert response.json() == test_part
    assert response.json()["location"] == test_location_template
    assert response.status_code == 200


# -------------------------- Read / GET -------------------------- #

def test_part_read_nonexistent():
    # TODO
    response = client.get("/parts/doesntexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "part with serial_number doesntexist does not exist"}


def test_part_read():
    # TODO
    assert False


# -------------------------- Update / PUT -------------------------- #


def test_part_update_with_nonexistent_category():
    # TODO
    assert False


def test_part_update_with_base_category():
    # TODO
    assert False


def test_part_update_correct():
    # TODO
    assert False


# -------------------------- Delete -------------------------- #


def test_part_delete_nonexistent():
    # TODO
    assert False


def test_part_delete():
    # TODO
    assert False
