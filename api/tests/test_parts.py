from fastapi.testclient import TestClient
import pytest
import mongomock

from ..main import app, get_db
from .example_data import fixture_part_1, fixture_part_2, fixture_deep_copy

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
    response = client.post(
        "/parts",
        json={"part": fixture_part_2, "location": fixture_part_2["location"]}
    )
    assert response.json() == fixture_part_2
    assert response.json()["location"] == fixture_part_2["location"]
    assert response.status_code == 200


# -------------------------- Add / POST -------------------------- #


def test_part_add_to_nonexistent_category():
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["category"] = "doesntexist"
    # Test trying to add nonexistent category
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_part["location"]}
    )
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_part_add_to_base_category():
    # Test trying to add to base category
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["category"] = "base_parts"
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_part["location"]}
    )
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_add_with_taken_location():
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["serial_number"] = "taken"
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_part["location"]}
    )
    assert response.json() == {"detail": "another part (serial: example_serial_no) is already at location: room='basement1' bookcase=1 shelf=1 cuvette=1 column=1 row=1"}
    assert response.status_code == 400


def test_part_add_correct():
    # Test trying to add to a valid part
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["location"]["row"] = 2
    test_part["serial_number"] = "qwerty"
    response = client.post(
        "/parts",
        json={"part": test_part, "location": test_part["location"]}
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
    # FIXME this probably fails because it doesn't deep compare the results?
    assert fixture_part_1 in response.json()
    assert fixture_part_2 in response.json()
    assert response.status_code == 200


def test_part_search():
    # TODO
    pass


# -------------------------- Update / PUT -------------------------- #


def test_part_update_with_nonexistent_category():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["serial_number"] = "blabla"
    new_part_data["category"] = "doesntexist"
    response = client.put(
        "/parts/example_serial_no",
        json={"new_part_data": new_part_data, "new_location": new_part_data["location"]}
    )
    assert response.json() == {"detail": "part category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_part_update_with_base_category():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["serial_number"] = "blabla"
    new_part_data["category"] = "base_parts"
    response = client.put(
        "/parts/example_serial_no",
        json={"new_part_data": new_part_data, "new_location": new_part_data["location"]}
    )
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_update_with_taken_location():
    # TODO
    pass


def test_part_update_correct():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["location"]["row"] = 7
    new_part_data["serial_number"] = "new_serial_no"
    response = client.put(
        "/parts/example_serial_no",
        json={"new_part_data": new_part_data, "new_location": new_part_data["location"]}
    )
    assert response.json() == new_part_data
    assert response.status_code == 200
    # Revert the change to not mess with other tests
    response = client.put(
        "/parts/new_serial_no",
        json={"new_part_data": fixture_part_1, "new_location": fixture_part_1["location"]}
    )
    assert response.json() == fixture_part_1
    assert response.status_code == 200


# -------------------------- Delete -------------------------- #


def test_part_delete_nonexistent():
    # TODO
    pass


def test_part_delete():
    # TODO
    pass
