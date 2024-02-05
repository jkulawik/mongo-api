from pydantic import BaseModel, Field

DEFAULT_MAX_LEN = 20


class Category(BaseModel):
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    # NOTE: on the db side, {"parent_id": ObjectID} is used to point to the appropriate category
    parent_name: str = Field(max_length=DEFAULT_MAX_LEN)


class Location(BaseModel):
    room: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    bookcase: int = Field(ge=1)
    shelf: int = Field(ge=1, le=6)
    cuvette: int = Field(ge=1, le=10)
    column: int = Field(ge=1, le=8)
    row: int = Field(ge=1, le=8)


class Part(BaseModel):
    serial_number: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    description: str = Field(max_length=50)
    # NOTE: on the db side, "category" is an ObjectID pointing to the appropriate category
    category: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    quantity: int = Field(ge=0)  # greater than or equal to 0
    price: float = Field(gt=0.0)  # greater than
    location: Location
