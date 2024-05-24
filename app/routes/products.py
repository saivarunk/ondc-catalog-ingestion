from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.dependencies import get_es_client
from app.core.models import BulkIngestPayload

router = APIRouter(prefix="/catalogs", tags=["products"])


@router.post("/{catalog_id}/products")
async def index_documents(catalog_id: str, payload: BulkIngestPayload, client=Depends(get_es_client)):
    response = client.index_documents(catalog_id, payload.records, payload.enable_vector_indexing)
    return JSONResponse(content={"data": response})
