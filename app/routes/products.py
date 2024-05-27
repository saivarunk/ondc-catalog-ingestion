from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.core.respository import create_product_bulk
from app.dependencies import get_es_client, mongo_db
from app.core.models import BulkIngestPayload
from app.celery import tasks

router = APIRouter(prefix="/catalogs", tags=["products"])


@router.post("/{catalog_id}/products")
async def index_documents(catalog_id: str, payload: BulkIngestPayload, client=Depends(get_es_client)):
    response = client.index_documents(catalog_id, payload.records, payload.enable_vector_indexing)
    mongo_response = create_product_bulk(mongo_db, catalog_id, payload.records)
    product_ids = [doc.index for doc in payload.records]
    if response['message'] == "Ingestion completed." and len(mongo_response['writeErrors']) == 0:
        tasks.process_catalog_ingestion.apply_async((catalog_id, product_ids))
        return JSONResponse(content={"data": response})
    else:
        return JSONResponse(content={"data": response}, status_code=400)


class ProductSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    brand: Optional[str] = None


@router.post("/{catalog_id}/products/search", description="Search products in a catalog")
async def product_search(catalog_id: str, request: ProductSearchRequest, client=Depends(get_es_client)):
    filters = {
        "category": request.category,
        "brand": request.brand
    }
    results = client.vector_search(catalog_id, "product", request.query, filters)
    return JSONResponse(content={"data": results})
