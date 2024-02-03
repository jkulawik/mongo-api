from fastapi.testclient import TestClient
from ..main import app
from .example_data import test_location_template, test_part_template

client = TestClient(app)


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
    # Create base category to add to
    response = client.post("/categories", json={"name": "category_abc", "parent_name": ""})
    assert response.status_code == 200
    # Test trying to add to base category
    response = client.post("/parts", json={
        "part": test_part_template,
        "location": test_location_template
        })
    assert response.json() == {"detail": "part can't be assigned to a base category (category_abc)"}
    assert response.status_code == 400


def test_part_add_correct():
    # Add base category and valid subcategory
    response = client.post("/categories", json={"name": "category_123", "parent_name": ""})
    assert response.status_code == 200
    response = client.post("/categories", json={
        "name": "category_456",
        "parent_name": "category_123"
        })
    assert response.status_code == 200
    # Test trying to add to a valid part
    test_part = test_part_template.copy()
    test_part["category"] = "category_456"
    response = client.post("/parts", json={
        "part": test_part,
        "location": test_location_template
        })
    assert response.json() == test_part
    assert response.status_code == 200
