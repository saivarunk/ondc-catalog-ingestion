from fastapi import APIRouter, Request, Response, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dependencies import get_es_client

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@router.post("/search", response_class=RedirectResponse, include_in_schema=False)
async def search(query: str = Form(...)):
    return f"/results?query={query}"


@router.post("/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, query: str, client=Depends(get_es_client)):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})


@router.get("/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, query: str, client=Depends(get_es_client)):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})


@router.get("/document_count", response_class=HTMLResponse, include_in_schema=False)
async def get_document_count(request: Request, client=Depends(get_es_client)):
    document_count, vector_count = client.get_document_count()
    return templates.TemplateResponse("document_count.html", {"request": request, "document_count": document_count,
                                                              "vector_count": vector_count})
