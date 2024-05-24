from fastapi import Depends, HTTPException, APIRouter
from pymongo import MongoClient
from pymongo.database import Database

from app.core.models import CatalogCreate, CatalogUpdate, CatalogInDB
from app.core.respository import create_catalog, get_catalogs, get_catalog, update_catalog, delete_catalog
from app.dependencies import mongo_db
from app.settings import settings

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.post("/", response_model=CatalogInDB)
def create_catalog_endpoint(catalog: CatalogCreate):
    catalog_id = create_catalog(mongo_db, catalog)
    return CatalogInDB(id=catalog_id, **catalog.dict())


@router.get("/", response_model=list[CatalogInDB])
def get_catalogs_endpoint():
    catalogs = get_catalogs(mongo_db)
    return [CatalogInDB(id=str(c["_id"]), name=c["name"]) for c in catalogs]


@router.get("/{catalog_id}", response_model=CatalogInDB)
def get_catalog_endpoint(catalog_id: str):
    catalog = get_catalog(mongo_db, catalog_id)
    if not catalog:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return CatalogInDB(id=str(catalog["_id"]), name=catalog["name"])


@router.put("/{catalog_id}", response_model=CatalogInDB)
def update_catalog_endpoint(catalog_id: str, catalog: CatalogUpdate):
    updated_count = update_catalog(mongo_db, catalog_id, catalog)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return CatalogInDB(id=catalog_id, **catalog.dict())


@router.delete("/{catalog_id}")
def delete_catalog_endpoint(catalog_id: str):
    deleted_count = delete_catalog(mongo_db, catalog_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return {"message": "Catalog deleted successfully"}
