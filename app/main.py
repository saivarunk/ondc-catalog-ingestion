import asyncio
from fastapi import FastAPI

from app.routes.views import router as views_router
from app.routes.products import router as product_router
from app.settings import settings


app = FastAPI(name=settings.app_name)

app.include_router(views_router)
app.include_router(product_router, prefix="/api/v1/products")
