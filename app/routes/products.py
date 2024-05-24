from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.dependencies import get_es_client
from app.core.models import BulkIngestPayload

router = APIRouter(prefix="/catlogs/{catalog_id}/products", tags=["products"])


@router.post("")
async def index_documents(payload: BulkIngestPayload, client=Depends(get_es_client)):
    response = client.index_documents(payload.records, payload.enable_vector_indexing)
    return JSONResponse(content={"data": response})
