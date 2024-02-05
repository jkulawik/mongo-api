from pymongo import database
from bson.objectid import ObjectId

fixture_part_1 = {
    "serial_number": "example_serial_no",
    "name": "Some Transistor",
    "description": "It has 3 legs.",
    "category": "test_parts",
    "quantity": 10,
    "price": 2.5,
    "location": {
        "room": "basement1",
        "bookcase": 1,
        "shelf": 1,
        "cuvette": 1,
        "column": 1,
        "row": 1,
    }
}

fixture_part_2 = {
    "serial_number": "q1w2e3",
    "name": "10 Ohm Resistor",
    "description": "Volts go brrrr",
    "category": "test_parts",
    "quantity": 5,
    "price": 3.0,
    "location": {
        "room": "basement1",
        "bookcase": 1,
        "shelf": 1,
        "cuvette": 2,
        "column": 4,
        "row": 7,
    }
}


fixture_part_3 = {
    "serial_number": "abcde",
    "name": "Condenser",
    "description": "Bulges and ruins your electronics.",
    "category": "test_parts",
    "quantity": 4,
    "price": 3.0,
    "location": {
        "room": "room2",
        "bookcase": 1,
        "shelf": 1,
        "cuvette": 2,
        "column": 4,
        "row": 7,
    }
}


fixture_part_4 = {
    "serial_number": "cvbbnm",
    "name": "brrrr",
    "description": "idk",
    "category": "new_parts",
    "quantity": 4,
    "price": 3.0,
    "location": {
        "room": "nowhere",
        "bookcase": 1,
        "shelf": 1,
        "cuvette": 2,
        "column": 4,
        "row": 7,
    }
}


fixture_part_5 = {
    "serial_number": "0451",
    "name": "GEP gun",
    "description": "Stealthy",
    "category": "new_parts",
    "quantity": 2,
    "price": 30.0,
    "location": {
        "room": "nowhere",
        "bookcase": 1,
        "shelf": 2,
        "cuvette": 2,
        "column": 4,
        "row": 7,
    }
}


def fixture_deep_copy(fixture: dict):
    copy = fixture.copy()
    copy["location"] = fixture["location"].copy()
    return copy


def add_test_data(db: database):
    # NOTE: fixtures aren't entered directly because user-side representation uses string names
    # and db side uses ObjectIDs to reference categories.
    # Similarly, db-side categories are created directly, without parent_name.
    base_parts = {"_id": ObjectId(), "name": "base_parts", "parent_id": None}
    test_parts = {"_id": ObjectId(), "name": "test_parts", "parent_id": base_parts["_id"]}
    new_parts = {"_id": ObjectId(), "name": "new_parts", "parent_id": base_parts["_id"]}

    edit_test_1 = {"_id": ObjectId(), "name": "edit_cat1", "parent_id": None}
    edit_test_2 = {"_id": ObjectId(), "name": "edit_cat2", "parent_id": edit_test_1["_id"]}
    edit_test_3 = {"_id": ObjectId(), "name": "edit_cat3", "parent_id": edit_test_1["_id"]}
    delete_test = {"_id": ObjectId(), "name": "deleteme", "parent_id": edit_test_1["_id"]}

    db.categories.insert_many([
        base_parts,
        test_parts,
        new_parts,
        edit_test_1,
        edit_test_2,
        edit_test_3,
        delete_test
    ])

    part_1 = fixture_deep_copy(fixture_part_1)
    part_1["category"] = test_parts["_id"]
    part_2 = fixture_deep_copy(fixture_part_2)
    part_2["category"] = test_parts["_id"]

    part_3 = fixture_deep_copy(fixture_part_1)
    part_3["category"] = edit_test_2["_id"]
    part_3["serial_number"] = "zxcasd"  # serial has to be unique
    part_3["location"]["room"] = "test_room"  # locations have to be unique
    part_3["name"] = "category test part"  # for testing readability

    part_4 = fixture_deep_copy(fixture_part_3)
    part_4["category"] = test_parts["_id"]

    part_5 = fixture_deep_copy(fixture_part_4)
    part_5["category"] = new_parts["_id"]
    part_6 = fixture_deep_copy(fixture_part_5)
    part_6["category"] = new_parts["_id"]

    db.parts.insert_many([part_1, part_2, part_3, part_4, part_5, part_6])
