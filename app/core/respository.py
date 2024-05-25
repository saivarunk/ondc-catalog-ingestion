from typing import List

from bson.objectid import ObjectId
from pymongo import UpdateOne
from pymongo.database import Database
from app.core.models import CatalogCreate, CatalogUpdate, Product


def get_catalog_collection(db: Database):
    return db["catalogs"]


def get_product_collection(db: Database):
    return db["products"]


def create_catalog(db: Database, catalog: CatalogCreate):
    catalog_collection = get_catalog_collection(db)
    catalog_dict = catalog.dict()
    result = catalog_collection.insert_one(catalog_dict)
    return str(result.inserted_id)


def create_product_bulk(db: Database, catalog_id: str, products: List[Product]):
    product_collection = get_product_collection(db)
    operations = []
    for product in products:
        product_dict = product.dict()
        product_dict["catalog_id"] = catalog_id
        product_dict["vector_indexed"] = False
        operations.append(
            UpdateOne(
                {"catalog_id": catalog_id, "index": product.index},
                {"$set": product_dict},
                upsert=True,
            )
        )
    result = product_collection.bulk_write(operations)
    print("result", result)
    return result.bulk_api_result


def get_products_by_catalog(db: Database, catalog_id: str):
    product_collection = get_product_collection(db)
    products = list(product_collection.find({"catalog_id": catalog_id}))
    return products


def get_product_by_ids(db: Database, catalog_id: str, product_ids: List[str]):
    product_collection = get_product_collection(db)
    products = list(
        product_collection.find({"catalog_id": catalog_id, "index": {"$in": product_ids}})
    )
    return products


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
