from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from .elastic_client import ElasticsearchClient

app = FastAPI()
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
es = Elasticsearch("https://localhost:9200", verify_certs=False, basic_auth=('elastic', 'pass@123'))

client = ElasticsearchClient("product_catalog", es, model)

# Templates setup
templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.post("/search", response_class=RedirectResponse)
async def search(query: str = Form(...)):
    # Perform Elasticsearch query here
    # For simplicity, we'll just return a redirect with the query in URL
    return f"/results?query={query}"


@app.post("/results", response_class=HTMLResponse)
async def show_results(request: Request, query: str):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})

@app.get("/results", response_class=HTMLResponse)
async def show_results(request: Request, query: str):
    results = client.vector_search("product", query)
    return templates.TemplateResponse("results.html", {"request": request, "query": query, "hits": results})