import requests

from pymongo import MongoClient
from elasticsearch import Elasticsearch

from app.settings import settings
from app.core.elastic_client import ElasticsearchClient


class Model:
    def encode(self, text):
        return requests.post("http://vector_service:5000/vectorize", json={"text": text}).json()


model = Model()

es = Elasticsearch(settings.es_host, verify_certs=False,
                   basic_auth=(settings.elastic_username, settings.elastic_password))

client = ElasticsearchClient(settings.es_index, es, model)

mongo_client = MongoClient(
    host=settings.mongo_host,
    port=settings.mongo_port,
    username=settings.mongo_user,
    password=settings.mongo_password,
)
mongo_db = mongo_client[settings.mongo_db]


async def get_es_client():
    yield client
