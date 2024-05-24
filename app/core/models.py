from pydantic import BaseModel
from typing import Optional, List


class Product(BaseModel):
    index: int
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
