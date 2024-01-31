
# NOTE this is unused

category_schema = {
    "bsonType": "object",
    "title": "Category object validation",
    "required": ["name", "parent_name"],
    "properties": {
        "name": {
            "bsonType": "string",
        },
        "parent_name": {
            "bsonType": "string",
            "description": "If empty, this is a base category. This will be used to create a category tree.",
        },
    }
}

location_schema = {
    "bsonType": "object",
    "title": "Location object validation",
    "required": ["room", "bookcase", "shelf", "cuvette", "column", "row"],
    "properties": {
        "room": {
            "bsonType": "string",
        },
        "bookcase": {
            "bsonType": "int",
            "minimum": 1,  # let's say bookcases are numbered per-room
        },
        "shelf": {
            "bsonType": "int",
            "minimum": 1,
            "maximum": 6,  # let's say we use standardised 6-shelf bookcases
        },
        "cuvette": {
            "bsonType": "string",
        },
        "column": {
            # Cuvettes can have different compartment sizes and thus varying numbers of columns and rows
            # hence only a minimum index check
            "bsonType": "int",
            "minimum": 1,
        },
        "row": {
            "bsonType": "int",
            "minimum": 1,
        },
    }
}

part_schema = {
    "bsonType": "object",
    "title": "Part object validation",
    "required": ["serial_number", "name", "description", "category", "quantity", "price", "location"],
    "properties": {
        "serial_number": {
            "bsonType": "string",
        },
        "name": {
            "bsonType": "string",
        },
        "description": {
            "bsonType": "string",
        },
        "category": {
            "bsonType": "string",
        },
        "quantity": {
            "bsonType": "int",
            "minimum": 0,
        },
        "price": {
            "bsonType": "double",
            "minimum": 0.01,
        },
        "location": {
            "$jsonschema": location_schema
        },
    }
}

parts_validator = {
    "$jsonschema": part_schema
}

categories_validator = {
    "$jsonschema": category_schema
}
