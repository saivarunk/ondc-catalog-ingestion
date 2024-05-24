from pydantic import BaseModel
from typing import Optional, List
from typing import Optional
from bson import ObjectId


class CatalogBase(BaseModel):
    name: str


class CatalogCreate(CatalogBase):
    pass


class CatalogUpdate(CatalogBase):
    pass


class CatalogInDB(CatalogBase):
    id: str

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str
        }


class Product(BaseModel):
    index: int
    catalog_id: Optional[str] = ""
    product: Optional[str]
    category: Optional[str]
    sub_category: Optional[str]
    brand: Optional[str]
    sale_price: Optional[float]
    market_price: Optional[float]
    type: Optional[str]
    rating: Optional[float]
    description: Optional[str]


class BulkIngestPayload(BaseModel):
    enable_vector_indexing: bool
    records: List[Product]
