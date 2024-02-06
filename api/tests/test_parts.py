from fastapi.testclient import TestClient
import mongomock

from ..main import app, get_db
from .example_data import fixture_part_1, fixture_part_2, fixture_part_3, fixture_part_4
from .example_data import fixture_deep_copy, add_test_data

client = TestClient(app)

test_client = mongomock.MongoClient()
test_db = test_client["test_db"]
add_test_data(test_db)


def override_db():
    try:
        yield test_db
    finally:
        pass


app.dependency_overrides[get_db] = override_db


# -------------------------- Add / POST -------------------------- #


def test_part_add_to_nonexistent_category():
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["category"] = "doesntexist"
    # Test trying to add nonexistent category
    response = client.post("/parts", json=test_part)
    assert response.json() == {"detail": "category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_part_add_to_base_category():
    # Test trying to add to base category
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["category"] = "base_parts"
    response = client.post("/parts", json=test_part)
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_add_with_taken_location():
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["serial_number"] = "taken"
    response = client.post("/parts", json=test_part)
    err_str = "another part (serial: example_serial_no) is already at location: "
    err_str += "room='basement1' bookcase=1 shelf=1 cuvette=1 column=1 row=1"
    assert response.json() == {"detail": err_str}
    assert response.status_code == 400


def test_part_add_correct():
    # Test trying to add to a valid part
    test_part = fixture_deep_copy(fixture_part_1)
    test_part["location"]["row"] = 2
    test_part["serial_number"] = "qwerty"
    response = client.post("/parts", json=test_part)
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


def test_part_search_by_serial():
    # Search a serial
    response = client.get("/parts?q=q1w2e3")
    assert response.status_code == 200
    assert fixture_part_1 not in response.json()
    assert fixture_part_2 in response.json()
    assert fixture_part_3 not in response.json()


def test_part_search_by_multiple():
    # Search in serial and name at the same time
    response = client.get("/parts?q=brr")
    assert response.status_code == 200
    assert fixture_part_1 not in response.json()
    assert fixture_part_2 in response.json()
    assert fixture_part_4 in response.json()


def test_part_search_by_room():
    # Search a location
    response = client.get("/parts?q=room")
    assert response.status_code == 200
    assert fixture_part_1 not in response.json()
    assert fixture_part_2 not in response.json()
    assert fixture_part_3 in response.json()


def test_part_search_by_description():
    # Search a description
    response = client.get("/parts?q=legs")
    assert response.status_code == 200
    assert fixture_part_1 in response.json()
    assert fixture_part_2 not in response.json()
    assert fixture_part_3 not in response.json()


def test_part_search_by_category():
    # Search a category name
    response = client.get("/parts?q=parts")
    assert response.status_code == 200
    assert fixture_part_1 in response.json()
    assert fixture_part_2 in response.json()
    assert fixture_part_3 in response.json()


# -------------------------- Update / PUT -------------------------- #


def test_part_update_with_nonexistent_category():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["serial_number"] = "blabla"
    new_part_data["category"] = "doesntexist"
    response = client.put("/parts/example_serial_no", json=new_part_data)
    assert response.json() == {"detail": "category {'name': 'doesntexist'} does not exist"}
    assert response.status_code == 404


def test_part_update_with_base_category():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["serial_number"] = "blabla"
    new_part_data["category"] = "base_parts"
    response = client.put("/parts/example_serial_no", json=new_part_data)
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_update_with_taken_location():
    # Try to update fixture 2 with fixture 1 location
    test_part = fixture_deep_copy(fixture_part_2)
    test_part["serial_number"] = "q1w2e3"
    test_part["location"] = fixture_part_1["location"].copy()
    response = client.put("/parts/q1w2e3", json=test_part)
    err_str = "another part (serial: example_serial_no) is already at location: "
    err_str += "room='basement1' bookcase=1 shelf=1 cuvette=1 column=1 row=1"
    assert response.json() == {"detail": err_str}
    assert response.status_code == 400


def test_part_update_correct():
    new_part_data = fixture_deep_copy(fixture_part_1)
    new_part_data["location"]["row"] = 7
    new_part_data["serial_number"] = "new_serial_no"
    response = client.put("/parts/example_serial_no", json=new_part_data)
    assert response.json() == new_part_data
    assert response.status_code == 200

    # Test if the part is updated in the db correctly
    response = client.get("/parts/new_serial_no")
    assert response.json() == new_part_data
    assert response.status_code == 200

    # Revert the change to not mess with other tests
    response = client.put("/parts/new_serial_no", json=fixture_part_1)
    assert response.json() == fixture_part_1
    assert response.status_code == 200


# -------------------------- Delete -------------------------- #


def test_part_delete_nonexistent():
    response = client.delete("/parts/doesntexist")
    assert response.status_code == 404
    assert response.json() == {"detail": "part {'serial_number': 'doesntexist'} does not exist"}


def test_part_delete():
    response = client.delete("/parts/q1w2e3")
    assert response.json() == {}
    assert response.status_code == 200

    # Test if the entry is correctly removed from the db
    response = client.get("/parts/q1w2e3")
    assert response.status_code == 404
    assert response.json() == {"detail": "part {'serial_number': 'q1w2e3'} does not exist"}
