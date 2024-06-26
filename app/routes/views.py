import io
import time

import pandas as pd
import urllib.parse

from fastapi import APIRouter, Request, Response, Depends, Form, UploadFile, File
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.core.models import CatalogCreate, Product
from app.core.respository import get_catalogs, create_catalog, get_catalog, create_product_bulk
from app.celery import tasks

from app.dependencies import get_es_client, mongo_db

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing_page(request: Request, client=Depends(get_es_client)):
    catalogs = get_catalogs(mongo_db)
    for catalog in catalogs:
        doc_count = client.get_document_count(str(catalog["_id"]))
        catalog['doc_count'] = doc_count

    return templates.TemplateResponse("landing.html", {"request": request, "catalogs": catalogs})


@router.get("/add-catalog", response_class=HTMLResponse)
async def get_add_catalog(request: Request):
    return templates.TemplateResponse("add_catalog.html", {"request": request})


@router.post("/add-catalog")
async def post_add_catalog(request: Request, name: str = Form(...)):
    payload = CatalogCreate(name=name)
    catalog_id = create_catalog(mongo_db, payload)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/index-catalog/{catalog_id}", response_class=HTMLResponse)
async def get_index_catalog(request: Request, catalog_id: str):
    return templates.TemplateResponse("index_catalog.html", {"request": request, "catalog_id": catalog_id})


@router.post("/index-catalog/{catalog_id}")
async def post_index_catalog(request: Request, catalog_id: str, file: UploadFile = File(...),
                             es_client=Depends(get_es_client)):
    catalog = get_catalog(mongo_db, catalog_id)

    if catalog is None:
        return HTMLResponse(content="Catalog not found", status_code=404)

    contents = await file.read()

    # measure time
    start = time.time()

    dataset = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    dataset['product'] = dataset['product'].fillna("")
    dataset['rating'] = dataset['rating'].fillna(0)
    dataset['description'] = dataset['description'].fillna("")
    dataset['brand'] = dataset['brand'].fillna("")

    documents = dataset.to_dict(orient="records")
    products = [Product(**doc) for doc in documents]

    # measure time
    end = time.time()
    print(f"Time taken to read and parse the file: {end - start} seconds")

    start = time.time()

    response = es_client.index_documents(catalog_id, products, False)

    end = time.time()
    print(f"Time taken to index the documents: {end - start} seconds")

    start = time.time()
    mongo_response = create_product_bulk(mongo_db, catalog_id, products)
    end = time.time()
    print(f"Time taken to write to MongoDB: {end - start} seconds")

    product_ids = [doc.index for doc in products]

    if response['message'] == "Ingestion completed." and len(mongo_response['writeErrors']) == 0:
        tasks.process_catalog_ingestion.apply_async((catalog_id, product_ids))
        return RedirectResponse(url=f"/", status_code=303)
    else:
        return HTMLResponse(content=response['message'], status_code=500)


@router.get("/products", response_class=HTMLResponse, include_in_schema=False)
async def paroduct_landing_page(request: Request):
    catalogs = get_catalogs(mongo_db)
    return templates.TemplateResponse("products.html", {"request": request, "catalogs": catalogs})


@router.post("/products/search", response_class=RedirectResponse, include_in_schema=False)
async def product_search(query: str = Form(...), catalog_id: str = Form(...), category: str = Form(""),
                         brand: str = Form("")):
    params = {
        "catalog_id": catalog_id,
        "query": query,
        "category": category,
        "brand": brand
    }
    encoded = urllib.parse.urlencode(params)
    return f"/products/results?{encoded}"


@router.post("/products/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, catalog_id: str, query: str, category: str, brand: str,
                       client=Depends(get_es_client)):
    catalogs = get_catalogs(mongo_db)
    filters = {
        "category": category,
        "brand": brand
    }
    results = client.vector_search(catalog_id, "product", query, filters)
    return templates.TemplateResponse("results.html", {"request": request,
                                                       "query": query,
                                                       "hits": results,
                                                       "catalogs": catalogs,
                                                       "catalog_id": catalog_id,
                                                       "category": category,
                                                       "brand": brand
                                                       })


@router.get("/products/results", response_class=HTMLResponse, include_in_schema=False)
async def show_results(request: Request, catalog_id: str, query: str, category: str, brand: str,
                       client=Depends(get_es_client)):
    catalogs = get_catalogs(mongo_db)
    filters = {
        "category": category,
        "brand": brand
    }
    results = client.vector_search(catalog_id, "product", query, filters)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results,
                                                       "catalogs": catalogs,
                                                       "catalog_id": catalog_id,
                                                       "category": category,
                                                       "brand": brand
                                                       })


@router.get("/document_count", response_class=HTMLResponse, include_in_schema=False)
async def get_document_count(request: Request, client=Depends(get_es_client)):
    document_count, vector_count = client.get_document_count()
    return templates.TemplateResponse("document_count.html", {"request": request, "document_count": document_count,
                                                              "vector_count": vector_count})
