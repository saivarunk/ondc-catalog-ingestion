from app.celery import celery_app
from app.dependencies import mongo_db, client as es_client


@celery_app.task
def process_catalog_ingestion(catalog_id: str):
    print(f"Processing catalog ingestion for catalog_id: {catalog_id}")
    return {"message": "Catalog ingestion completed."}
