from pydantic import BaseModel, Field

DEFAULT_MAX_LEN = 20


class Category(BaseModel):
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    parent_name: str = Field(max_length=DEFAULT_MAX_LEN)


class Part(BaseModel):
    serial_number: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    name: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    description: str = Field(max_length=50)
    category: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    quantity: int = Field(ge=0)  # greater than or equal to 0
    price: float = Field(gt=0.0)  # greater than

    # location: dict
    # NOTE: location is handled by the API as another model (right below), but inserted into the db
    # after validation


class Location(BaseModel):
    """
    Ideally locations would be a DB collection where we could validate individual dimensions
    of each cuvette and bookcase, as well as check if target location actually exists.
    Perhaps even label each cuvette unique names and then assign location as a cuvette name,
    whose location can then be looked up in the db. This would also be much easier when
    cuvettes need to be moved.

    For now though let's pretend that every cuvette, shelf and bookcase have standardized sizes.
    For example, 6 shelves per bookcase and 8x8 cuvettes. Using indexes counted from 1 because
    that's probably what non-programmers would do in a warehouse.
    """
    room: str = Field(min_length=1, max_length=DEFAULT_MAX_LEN)
    bookcase: int = Field(ge=1)
    shelf: int = Field(ge=1, le=6)
    cuvette: int = Field(ge=1, le=10)
    column: int = Field(ge=1, le=8)
    row: int = Field(ge=1, le=8)
