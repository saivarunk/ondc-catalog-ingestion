from bson.objectid import ObjectId
from pymongo.database import Database
from app.core.models import CatalogCreate, CatalogUpdate


def get_catalog_collection(db: Database):
    return db["catalogs"]


def create_catalog(db: Database, catalog: CatalogCreate):
    catalog_collection = get_catalog_collection(db)
    catalog_dict = catalog.dict()
    result = catalog_collection.insert_one(catalog_dict)
    return str(result.inserted_id)


def get_catalogs(db: Database):
    catalog_collection = get_catalog_collection(db)
    catalogs = list(catalog_collection.find())
    return catalogs


def get_catalog(db: Database, catalog_id: str):
    catalog_collection = get_catalog_collection(db)
    catalog = catalog_collection.find_one({"_id": ObjectId(catalog_id)})
    return catalog


def update_catalog(db: Database, catalog_id: str, catalog: CatalogUpdate):
    catalog_collection = get_catalog_collection(db)
    result = catalog_collection.update_one(
        {"_id": ObjectId(catalog_id)}, {"$set": catalog.dict()}
    )
    return result.modified_count


def delete_catalog(db: Database, catalog_id: str):
    catalog_collection = get_catalog_collection(db)
    result = catalog_collection.delete_one({"_id": ObjectId(catalog_id)})
    return result.deleted_count
