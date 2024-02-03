from fastapi.testclient import TestClient
import pytest
from ..main import app
from .example_data import test_location_template, test_part_template

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def init_data_for_parts_testing():
    # Add base category and subcategory
    response = client.post("/categories", json={"name": "base_parts", "parent_name": ""})
    assert response.status_code == 200
    response = client.post("/categories", json={"name": "test_parts", "parent_name": "base_parts"})
    assert response.status_code == 200


def test_part_add_to_nonexistent_category():
    test_part = test_part_template.copy()
    test_part["category"] = "doesntexist"
    # Test trying to add nonexistent category
    response = client.post("/parts", json={
        "part": test_part,
        "location": test_location_template
        })
    assert response.json() == {"detail": "part category doesntexist does not exist"}
    assert response.status_code == 400


def test_part_add_to_base_category():
    # Test trying to add to base category
    response = client.post("/parts", json={
        "part": test_part_template,
        "location": test_location_template
        })
    assert response.json() == {"detail": "part can't be assigned to a base category (base_parts)"}
    assert response.status_code == 400


def test_part_add_correct():
    # Test trying to add to a valid part
    test_part = test_part_template.copy()
    test_part["category"] = "test_parts"
    response = client.post("/parts", json={
        "part": test_part,
        "location": test_location_template
        })
    # Location is not a part of the Part model: like in the API, it has to be added to JSON manually
    test_part["location"] = test_location_template
    assert response.json() == test_part
    assert response.json()["location"] == test_location_template
    assert response.status_code == 200
