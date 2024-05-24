from pymongo import MongoClient
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from app.settings import settings
from app.core.elastic_client import ElasticsearchClient

model = SentenceTransformer('l3cube-pune/indic-sentence-similarity-sbert')
es = Elasticsearch(settings.es_host, verify_certs=False,
                   basic_auth=(settings.elastic_username, settings.elastic_password))

client = ElasticsearchClient("product_catalog_indic", es, model)


async def get_es_client():
    yield client


def get_mongo_client():
    client = MongoClient(
        host=settings.mongo_host,
        port=settings.mongo_port,
        username=settings.mongo_user,
        password=settings.mongo_password,
    )
    try:
        yield client
    finally:
        client.close()
