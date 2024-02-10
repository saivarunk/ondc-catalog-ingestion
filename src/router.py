from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


from models import BulkIngestPayload
from dependencies import get_es_client

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@router.post("/search", response_class=RedirectResponse, include_in_schema=False)
async def search(query: str = Form(...)):
    return f"/results?query={query}"


@router.post("/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, query: str, client = Depends(get_es_client)):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})

@router.get("/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, query: str, client = Depends(get_es_client)):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})

@router.post("/documents/index")
async def index_documents(payload: BulkIngestPayload, client = Depends(get_es_client)):
    response = client.index_documents(payload.records, payload.enable_vector_indexing)
    return JSONResponse(content={"data": response})

@router.get("/document_count", response_class=HTMLResponse)
async def get_document_count(request: Request, client = Depends(get_es_client)):
    document_count, vector_count = client.get_document_count()
    return templates.TemplateResponse("document_count.html", {"request": request, "document_count": document_count, "vector_count": vector_count})
