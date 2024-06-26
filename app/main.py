import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.templating import Jinja2Templates

from app.routes.views import router as views_router
from app.routes.products import router as product_router
from app.routes.catalogs import router as catalog_router
from app.settings import settings

app = FastAPI(name=settings.app_name, version="0.1.0")

app.include_router(views_router)
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="app/templates/images"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Exception: {str(exc)}")
    return templates.TemplateResponse("error.html", {"request": request, "detail": str(exc)},
                                      status_code=HTTP_500_INTERNAL_SERVER_ERROR)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version="0.1.0",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://ondc.org/assets/theme/images/ondc_registered_logo.svg?v=d15e6043c5"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
