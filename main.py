from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

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
    """The path parameter type will help you match any path, including /, /path/to/file.txt, etc."""
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


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    """Adding default values will automatically be made query parameters."""
    return fake_items_db[skip : skip + limit]


class Item(BaseModel):
    """Pydantic models will be used to validate the request body."""

    name: str
    description: str | None = None
    price: float
    tax: int | None = None


@app.post("/items/")
async def create_item(item: Item):
    some_value = item.name
    return some_value
