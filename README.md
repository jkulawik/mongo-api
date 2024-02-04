
# Setup

Optional: create and activate a virtual environment:
- Create: `python -m venv .venv`
- Activate:
  - On Windows: `.venv\Scripts\activate.bat`
  - On Linux: `source .venv/bin/activate`

Install requirements:
```pip install -r requirements.txt```

The app requires a `connect_info.txt` file in the run directory.
First line should contain a MongoDB connection string, and the 2nd one - a database name.
For example:
```
mongodb+srv://123456@xxxx.zzzz.mongodb.net
example_database_name
```

This approach means that secrets aren't stored on the repo
and removes the need of entering this data during each app launch.

# Usage

Testing: run `pytest` in the project folder.

Run the app with:
```uvicorn api.main:app --reload```

In the console output, note the API URI (default: `http://127.0.0.1:8000`).
Swagger docs of the API are available at `http://127.0.0.1:8000/docs`.
All endpoints and methods are listed there,
but a simplified API documentation is available in this markdown file.

# Project specification

- Create an API with CRUD functionality for two MongoDB collections: Parts and Categories.
- Validate input using object models. A list of mandatory fields was supplied.
- Parts collection:
  - Ensure that each part belongs to a category and that a part cannot be in a base category.
  - Create an additional endpoint
- Categories collection:
  - Ensure that a category cannot be removed if there are parts assigned to it.
  - Ensure that a parent category cannot be removed if it has child categories with parts assigned.
- Return results in JSON format so that they can be consumed with Postman.
- Dockerize the app.


# Design

The FastAPI framework was chosen over Flask due to bigger familiarity and a more complete feature set.

## Data validation

Basic validation (whether all mandatory fields are present, string length, min/max values)
is handled by FastAPI and Pydantic.
As such, some of the basic validation isn't checked explicitly.
For example, making sure that all parts belong to a category:
the app always requires the user to supply one that's not empty.

## Locations

To simplify work with part location, location was given its own object model and is POSTed as a separate JSON in the request body.
After validation, this data is appended to Part data as a dictionary to comply with the specified API schema.

Since no requirements were listed about the location data, an idealised warehouse model was assumed: every cuvette, shelf and bookcase have the same sizes (6 shelves per bookcase and 8x8 cuvettes). Indexes in these are counted from 1 because
that's probably what non-programmers would do in a warehouse.
Room names are arbitrary and bookcase counts don't have an upper limit.

## Document IDs

In several places, `del document["_id"]` is used because
PyMongo uses ObjectID instances instead of raw IDs.
These objects crash FastAPI and pytest because they're not serialisable,
and since database IDs are not required by the end user they can be simply removed from the output.

## Categories

At first, categories were referenced by their name in other documents.
This approach was naive because it restricts the option to update categories,
and creates opportunities for Parts to reference nonexistent categories.

To improve this, the app now internally (including in the database) uses ObjectIDs
whenever a category is referenced
(i.e. both in Parts documents and the parent field in Category documents).

This means that categories can be renamed when they have parts assigned.
Category data still has to be validated when updating though:
- test name uniqueness
- whether the parent is not being set to self
- whether parent exists

As per specification, the end user should get and provide category names.
To this end, the IDs are replaced with names when returning data and vice versa when receiving it.
Category parents use different fields for this (`parent_id` and `parent_name`).
The category field in parts uses the same field for both, which is incidental on the fact
that specification asks for a field simply called `category`'
(whereas `parent_name` clashed with using it for an ID).


## Proposals

While this is out of scope and would complicate the project, making Locations their own Mongo collection would likely simplify warehouse operations.

A naive approach would be to label each cuvette with a unique name and then reference cuvettes in Parts objects.
This would make moving cuvettes much easier and would decouple location maintenance from the Parts collection.

# API documentation

TODO