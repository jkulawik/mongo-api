from fastapi.testclient import TestClient
from fastapi import status
from main import app

client = TestClient(app)


def test_category_add():
    # Test FastAPI's type and model validation
    response = client.post("/categories", json={"name": ""})  # missing parameter
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = client.post("/categories", json={"name": 2, "parent_name": ""})  # wrong type
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = client.post("/categories", json={"name": "", "parent_name": ""})  # empty name
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Test self-referencing category
    response = client.post("/categories", json={"name": "resistors", "parent_name": "resistors"})
    assert response.json() == {"detail": "category parent name can't be same as category name"}
    assert response.status_code == 400
    # Test regular add of root category
    response = client.post("/categories", json={"name": "abc", "parent_name": ""})
    assert response.json() == {"detail": "created successfully"}
    assert response.status_code == 200
    # Test trying to add duplicates
    response = client.post("/categories", json={"name": "abc", "parent_name": ""})
    assert response.json() == {"detail": "category abc already exists"}
    assert response.status_code == 409
    # Test adding a category with nonexistent parent
    response = client.post("/categories", json={"name": "xyz", "parent_name": "qwop"})
    assert response.json() == {"detail": "parent category with name qwop does not exist"}
    assert response.status_code == 400
    # Test add a category with valid parent
    response = client.post("/categories", json={"name": "xyz", "parent_name": "abc"})
    assert response.json() == {"detail": "created successfully"}
    assert response.status_code == 200


def test_category_read():
    response = client.get("/categories/test_category")
    assert response.status_code == 404
    # Create an entry to get
    client.post("/categories", json={"name": "test_category", "parent_name": ""})
    # Test basic get
    response = client.get("/categories/test_category")
    assert response.json() == {"name": "test_category", "parent_name": ""}
    assert response.status_code == 200
    # Add 2nd category for next test
    client.post("/categories", json={"name": "test_category2", "parent_name": ""})
    # Test the all categories endpoint
    response = client.get("/categories")
    assert {"name": "test_category", "parent_name": ""} in response.json() and {"name": "test_category2", "parent_name": ""} in response.json()
    assert response.status_code == 200


def test_category_update():
    # TODO test category update
    pass


def test_category_delete():
    # TODO test category delete
    pass
