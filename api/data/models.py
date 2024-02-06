from pydantic import BaseModel, Field

DEFAULT_MAX_LEN = 20


class Category(BaseModel):
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN, default="name")
    # NOTE: on the db side, {"parent_id": ObjectID} is used to point to the appropriate category
    # and parent_name is removed
    parent_name: str = Field(max_length=DEFAULT_MAX_LEN, default="parent_name")


class Location(BaseModel):
    """
    Since no requirements were listed about the location data,
    an idealised warehouse model was assumed: every cuvette,
    shelf and bookcase have the same sizes (6 shelves per bookcase and 8x8 cuvettes).
    
    Indexes in these are counted from 1 because
    that's probably what non-programmers would do in a warehouse.

    Room names are arbitrary and bookcase counts don't have an upper limit.
    """
    room: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN, default="room")
    bookcase: int = Field(ge=1, default=1)
    shelf: int = Field(ge=1, le=6, default=1)
    cuvette: int = Field(ge=1, le=10, default=1)
    column: int = Field(ge=1, le=8, default=1)
    row: int = Field(ge=1, le=8, default=1)


class Part(BaseModel):
    serial_number: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN, default="1234")
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN, default="part_name")
    description: str = Field(max_length=50, default="Part description")
    # NOTE: on the db side, "category" is an ObjectID pointing to the appropriate category
    category: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN, default="category")
    quantity: int = Field(ge=0, default=10)  # greater than or equal to 0
    price: float = Field(gt=0.0, default=2.0)  # greater than
    location: Location
