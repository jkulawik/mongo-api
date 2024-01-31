uvicorn api.main:app --reload
pytest

Data validation in MongoDB was considered, but FastAPI/Pydantic was chosen due to higher flexibility.
Pydantic's Field

Areas that could use improvement:
- testing uses the "production" database instead of a mock
- testing probably shouldn't be stateful: the database is emptied on each app start, but data persists between tests
- locations could be a MongoDB collection with their own validation, but this was out of project scope
