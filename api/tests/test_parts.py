from fastapi.testclient import TestClient
import pytest
import mongomock

from ..main import app, get_db
from .example_data import fixture_part_1, fixture_part_2

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
def init_data_for_parts_testing():
    # Add base category and subcategory
    response = client.post("/categories", json={"name": "base_parts", "parent_name": ""})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "test_parts", "parent_name": "base_parts"})
    assert response.status_code == 200
    # Add test parts
    response = client.post(
        "/parts",
        json={"part": fixture_part_1, "location": fixture_part_1["location"]}
    )
    assert response.json() == fixture_part_1
    assert response.json()["location"] == fixture_part_1["location"]
    assert response.status_code == 200


# -------------------------- Add / POST -------------------------- #


def test_part_add_to_nonexistent_category():
    test_part = fixture_part_1.copy()
    test_part["category"] = "doesntexist"
    # Test trying to add nonexistent category
    response = client.post(
        "/parts",
        json={"part": test_part, "location": fixture_part_1["location"]}
    )
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_part_add_to_base_category():
    # Test trying to add to base category
    test_part = fixture_part_1.copy()
    test_part["category"] = "base_parts"
    response = client.post(
        "/parts",
        json={"part": test_part, "location": fixture_part_1["location"]}
    )
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_add_correct():
    # Test trying to add to a valid part
    test_part = fixture_part_1.copy()
    response = client.post(
        "/parts",
        json={"part": test_part, "location": fixture_part_1["location"]}
    )
    assert response.json() == test_part
    assert response.status_code == 200


# -------------------------- Read / GET -------------------------- #

def test_part_read_nonexistent():
    response = client.get("/parts/doesntexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "part {'serial_number': 'doesntexist'} does not exist"}


def test_part_read():
    response = client.get("/parts/example_serial_no")
    assert response.json() == fixture_part_1
    assert response.status_code == 200


def test_part_read_many():
    response = client.get("/parts")
    assert fixture_part_1 in response.json()
    assert fixture_part_2 in response.json()
    assert response.status_code == 200


def test_part_search():
    # TODO
    pass


# -------------------------- Update / PUT -------------------------- #


def test_part_update_with_nonexistent_category():
    # TODO
    pass


def test_part_update_with_base_category():
    # TODO
    pass


def test_part_update_correct():
    # TODO
    pass


# -------------------------- Delete -------------------------- #


def test_part_delete_nonexistent():
    # TODO
    pass


def test_part_delete():
    # TODO
    pass
