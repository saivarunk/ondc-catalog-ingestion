from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from settings import settings

from elastic_client import ElasticsearchClient

model = SentenceTransformer('l3cube-pune/indic-sentence-similarity-sbert')
es = Elasticsearch(settings.es_host, verify_certs=False, basic_auth=(settings.elastic_username, settings.elastic_password))

client = ElasticsearchClient("product_catalog_indic", es, model)

async def get_es_client():
    yield client
