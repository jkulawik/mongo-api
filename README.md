
# Setup

Optional: create and activate a virtual environment:
- Create: `python -m venv .venv`
- Activate:
  - On Windows: `.venv\Scripts\activate.bat`
  - On Linux: `source .venv/bin/activate`

Install requirements:
```
pip install -r requirements.txt
```

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
```
uvicorn api.main:app
```

In the console output, note the API URI (default: `http://127.0.0.1:8000`).
Swagger docs of the API are available at `http://127.0.0.1:8000/docs`.
All endpoints and methods are listed there,
but a simplified API documentation is available in this markdown file.

# As a Docker container

Make sure the `connect_info.txt` file in the project folder contains valid connection data before building.

Build image:
```
docker build -t mongo-crud-api .
```

Run container:
```
docker run -p 80:80 mongo-crud-api
```

Press `Ctrl+C` in the terminal window to stop the container.

The API should be available at the IP address of your Docker interface
(check `ip a` on Linux or `ipconfig` on Windows).
Ideally, try the `/docs` endpoint in your browser.

# Project specification

- Create an API with CRUD functionality for two MongoDB collections: Parts and Categories.
- Validate input using object models. A list of mandatory fields was supplied.
- Parts collection:
  - Ensure that each part belongs to a category and that a part cannot be in a base category.
  - Create an additional endpoint for searching parts with any of the part properties.
- Categories collection:
  - Ensure that a category cannot be removed if there are parts assigned to it.
  - Ensure that a parent category cannot be removed if it has child categories with parts assigned.
- Return results in JSON format so that they can be consumed with Postman.
- Dockerize the app.


# Design

The FastAPI framework was chosen over Flask due to bigger familiarity and a more complete feature set.

The app uses 3 data models: Category, Location and Part. Location is nested in the Part model.

## Data validation

Basic validation (whether all mandatory fields are present, string length, min/max values)
is handled by FastAPI and Pydantic.

Asides from the validation from the specification, the app also checks:
- category name and part serial number uniqueness
- whether a category parent is not being set to self
- in each operation involving fetching categories by name: whether a category with such name exists
- if a part is not being assigned to a location which is already in use by another part
- all of the appropriate validation rules when a part or a category is being updated

## Categories and ObjectIDs

To enable editing category data without invalidating other Mongo documents,
the app internally uses ObjectIDs whenever a category is referenced
(i.e. both in Parts documents and the parent field in Category documents).

As per specification, the end user should use category names as strings.
To this end, the IDs are replaced with names when returning data and vice versa when receiving it:
- Since the specification asks for a field simply called `category` in the Parts model, it gets simply replaced with the right data type.
- Because the Category model should use `parent_name`,
this field is removed and `parent_id` is inserted instead when an ObjectID is needed (and vice versa).

# API documentation

TODO