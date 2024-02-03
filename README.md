uvicorn api.main:app --reload
pytest


Areas that could use improvement:
- testing uses the "production" database instead of a mock
- testing probably shouldn't be stateful: the database is emptied on each app start, but data persists between tests
- locations could be a MongoDB collection with their own validation, but this was out of project scope


# Design

## Data validation

MongoDB data validation was considered, but FastAPI/Pydantic was chosen due to higher flexibility.
Basic validation (whether all mandatory fields are present, string length, min/max values)
is handled by FastAPI and Pydantic's Field.
As such, some of the basic validation isn't checked explicitly.
For example, making sure that all parts belong to a category:
the app always requires the user to supply one that's not empty.

## Document IDs
In several places, `del document["_id"]` is used.
PyMongo uses ObjectID instances instead of raw IDs.
These objects crash FastAPI and pytest because they're not serialisable,
and since database IDs are not needed by the end user they are just removed.
Worth noting is that pymongo not only returns dictionaries with ObjectIDs,
but also inserts them into the dictionaries which are used in pymongo function arguments.