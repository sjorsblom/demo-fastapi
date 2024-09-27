from dataclasses import dataclass
from enum import Enum
from typing import Annotated, NotRequired, TypedDict

from fastapi import (
    Body,
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/")
async def root():
    """Only single line comments are supported in FastAPI."""
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/idk/{user_id}")
async def idk(user_id: str):
    return {"idk": user_id}


@app.get("/users/other/{user_id}")
async def read_another_user(user_id: str):
    return {"user_id": user_id}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """The path parameter type will help you match any path, including /,
    /path/to/file.txt, etc."""
    return {"file_path": file_path}


class ModelName(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.ALEXNET:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    """Pydantic models will be used to validate the request body."""

    name: str
    description: str | None = Field(default=None, max_length=300)
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item2",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """The status_code parameter will set the response status code."""
    some_value = item.name
    return some_value


class Results(TypedDict):
    q: NotRequired[str | None]
    items: list[dict[str, str]]


@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None
):
    """Query parameters will be validated using the Query class.
    This can make serialization easy and clean."""
    results: Results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items_multiple_q/{item_id}")
async def read_items_multiple_q(
    item_id: Annotated[int, Path(gt=0)],
    q: Annotated[
        list[str] | None,
        Query(deprecated=True),
    ] = None,
    hidden_q: Annotated[
        str | None,
        Query(include_in_schema=False),
    ] = None,
):
    query_items = {"q": q, "hidden_q": hidden_q, "item_id": item_id}
    return query_items


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    """The Body class embed parameter will add the key 'item' to the request body.
    (Only needed for singular body parameters)"""
    results = {"item_id": item_id, "item": item}
    return results


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """The UploadFile class will help you handle file uploads."""
    if file.content_type != "image/jpeg":
        # Example of raising an HTTPException with a custom status code and detail.
        # Also, custom headers can be added.
        raise HTTPException(
            status_code=400,
            detail="Only JPEG allowed",
            headers={"X-Error": "There goes my error"},
        )
    return {"filename": file.filename}


# You can catch a specific exception and globally handle it.
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get(
    "/unicorns/{name}",
    tags=["default", "unicorns"],
    summary="Create an item with a cool title",
    description="Create an item with all the information, name, description, price, \
        tax and a set of unique tags",
)
async def read_unicorn(name: str):
    """The function description will be overwritten by the description parameter."""
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


@app.get(
    "/cool/description", response_description="The cool description in the response"
)
async def cool_description():
    """
    Create an item with all the information:
    This description will use markdown formatting.

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return {"description": "This is a cool description."}


@app.get(
    "/cool/description_deprecated",
    response_description="The cool description in the response",
    deprecated=True,
)
async def cool_description_deprecated():
    """
    You can use the deprecated parameter to mark a route as deprecated.
    """
    return {"description": "This is a cool description."}


fake_db = {}


class ItemFake(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


@app.put("/json/items/{id}")
def update_item_fake(id: str, item: ItemFake):
    """
    In this example, it would convert the Pydantic model to a dict,
    and the datetime to a str.
    """
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data


db_items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.patch("/patching_items/{item_id}", response_model=ItemFake)
async def update_item_fake_db(item_id: str, item: ItemFake):
    stored_item_data = db_items[item_id]
    if not isinstance(stored_item_data, dict):
        raise TypeError("stored_item_data must be a dictionary")
    stored_item_model = ItemFake(**stored_item_data)
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    db_items[item_id] = jsonable_encoder(updated_item)
    return updated_item


async def pagination_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/paginated_items", response_model=ItemFake)
async def paginated_items(pagination: Annotated[dict, Depends(pagination_parameters)]):
    return pagination


@app.get("/paginated_users/")
async def paginated_users(pagination: Annotated[dict, Depends(pagination_parameters)]):
    return pagination


PaginationDep = Annotated[dict, Depends(pagination_parameters)]


@app.get("/alternative_paginated_items", response_model=ItemFake)
async def alternative_paginated_items(pagination: PaginationDep):
    return pagination


@app.get("/alternative_paginated_users/")
async def alternative_paginated_users(pagination: PaginationDep):
    return pagination


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/query_params/items/")
async def read_items_query_params(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response


@dataclass
class CommonQueryParamsDataClass:
    q: str | None = None
    skip: int = 0
    limit: int = 100


@app.get("/query_params_data_class/items/")
async def read_items_query_params_dat_class(
    commons: Annotated[CommonQueryParamsDataClass, Depends()]
):
    """Dataclasses look cleaner and seem to work too."""
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
