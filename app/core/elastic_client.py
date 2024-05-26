from typing import List

from elasticsearch import helpers
from pymongo import MongoClient

from app.core.models import Product
from app.settings import settings

mongo_client = MongoClient(
    host=settings.mongo_host,
    port=settings.mongo_port,
    username=settings.mongo_user,
    password=settings.mongo_password,
)
mongo_db = mongo_client[settings.mongo_db]


class ElasticsearchClient:
    supported_keys = [
        "product",
        "description",
    ]

    keyword_keys = [
        "category",
        "sub_category",
        "brand",
        "type"
    ]

    def __init__(self, index_name, client, model) -> None:
        self.index_name = index_name
        self.client = client
        self.model = model

    def vector_search(self, catalog_id, field, question, filters: dict = None):
        # query_vector_product = self.model.encode(question)
        script_query = {
            "bool": {
                "must": [
                    {"term": {"catalog_id": catalog_id}},
                    {
                        "multi_match": {
                            "query": question,
                            "fields": ["product", "product_hi", "product_te", "product_gu", "product_ka", "product_bn", "product_mr"]
                        }
                    }
                ]
            }
        }
        if filters:
            filter_clause = [
                {
                    "term": {
                        k: v
                    }
                }
                for k, v in filters.items()
                if v
            ]
            if filter_clause and len(filter_clause) > 0:
                script_query["bool"]["filter"] = filter_clause
        print("====query:", script_query)
        response = self.client.search(
            index=self.index_name, body={"query": script_query}
        )
        return response["hits"]["hits"]

    def index_documents(self, catalog_id: str, documents: List[Product], enable_vector_indexing=False):
        translation_collection = mongo_db["product_translation_cache"]
        actions = []
        for document in documents:
            document.catalog_id = catalog_id
            action = {
                "_index": self.index_name,
                "_id": f"{catalog_id}_{document.index}",
                "_source": document.dict(),
            }
            if enable_vector_indexing:
                # get translation using product.product as key in translation collection
                translation = translation_collection.find_one({"key": document.product})
                if translation:
                    action["_source"]["product_hi"] = translation.get("hi", "")
                    action["_source"]["product_ka"] = translation.get("ka", "")
                # for key, value in document.dict().items():
                #     if key in self.supported_keys and value:
                #         dense_vectors = self.model.encode(value)
                #         if len(dense_vectors) > 0:
                #             action["_source"][f"{key}_dense_vector"] = dense_vectors
            print(action)
            actions.append(action)

        try:
            response = helpers.bulk(self.client, actions)
            if response[0] == len(documents):
                return {"message": "Ingestion completed."}
            else:
                raise Exception(
                    f"Failed to ingest {len(documents) - response[0]} documents."
                )
        except Exception as e:
            return {"error": e}

    def get_document_count(self, catalog_id):
        doc_query = {
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "product"}}
                    ],
                    "filter": [
                        {"term": {"catalog_id": catalog_id}}
                    ]
                }
            }
        }
        vector_query = {
            "query": {
                "bool": {
                    "must": [
                        {"exists": {"field": "product_hi"}}
                    ],
                    "filter": [
                        {"term": {"catalog_id": catalog_id}}
                    ]
                }
            }
        }
        doc_res = self.client.count(index=self.index_name, body=doc_query)
        vector_res = self.client.count(index=self.index_name, body=vector_query)
        return doc_res["count"], vector_res["count"]
