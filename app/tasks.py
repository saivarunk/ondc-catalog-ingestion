from pymongo import UpdateOne

from app.celery import celery_app
from app.core.models import Product
from app.dependencies import mongo_db, client as es_client
from app.core.respository import get_products_by_catalog


@celery_app.task
def process_catalog_ingestion(catalog_id: str):
    print(f"Processing catalog ingestion for catalog_id: {catalog_id}")
    db_products = get_products_by_catalog(mongo_db, catalog_id)
    products_to_index = [Product(**doc) for doc in db_products]

    batch_size = 100
    for i in range(0, len(products_to_index), batch_size):
        batch = products_to_index[i:i + batch_size]
        response = es_client.index_documents(catalog_id, batch, True)
        if response['message'] == "Ingestion completed.":
            print(f"Catalog ingestion completed for catalog_id: {catalog_id}")

        else:
            print(f"Catalog ingestion failed for catalog_id: {catalog_id}")
            raise Exception(f"Catalog ingestion failed for catalog_id: {catalog_id}")
