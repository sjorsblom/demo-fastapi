from enum import Enum
from functools import lru_cache
from typing import Annotated, Dict, List, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, BeforeValidator, Field
from motor.motor_asyncio import AsyncIOMotorClient
import config


app = FastAPI()


@lru_cache
def get_settings():
    return config.Settings()


PyObjectId = Annotated[str, BeforeValidator(str)]


class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    ean: str
    order_ean: str
    nummerartikel: int
    productselection: str
    posartikel: int
    price: float
    quantity: str
    images: List[str]
    url: str
    title: str
    assortment_code: List[str]
    assortment_category: List[str]
    code: str
    description: List[str]
    gebruik: str
    recept: Dict[str, float]
    pigments: Dict[str, float]
    veiligheid: Dict[str, str]


@app.get("/product/{ean}", response_model=Product)
async def read_user(
    ean: str, settings: Annotated[config.Settings, Depends(get_settings)]
):
    # print(os.environ)
    print(settings)
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client.get_database("grimas")
    products_collection = db.get_collection("products")

    product = await products_collection.find_one({"ean": ean})

    print(product)

    return product
