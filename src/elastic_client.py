from typing import List

from elasticsearch import helpers
from models import Product


class ElasticsearchClient:

    supported_keys = [
        "product",
        "category",
        "sub_category",
        "brand",
        "description",
        "type",
    ]

    def __init__(self, index_name, client, model) -> None:
        self.index_name = index_name
        self.client = client
        self.model = model

    def vector_search(self, field, question):
        query_vector_product = self.model.encode(question)
        print(query_vector_product)
        script_query = {
            "script_score": {
                "min_score": 1.3,
                "query": {
                    "bool": {"must": [{"exists": {"field": "product_dense_vector"}}]}
                },
                "script": {
                    "source": f"cosineSimilarity(params.query_vector, '{field}_dense_vector') + 1.0",
                    "params": {"query_vector": query_vector_product.tolist()},
                },
            }
        }
        response = self.client.search(
            index=self.index_name, body={"query": script_query}
        )
        return response["hits"]["hits"]

    def index_documents(self, documents: List[Product], enable_vector_indexing=False):
        actions = []
        for document in documents:
            action = {
                "_index": self.index_name,
                "_id": document.index,
                "_source": document.dict(),
            }
            if enable_vector_indexing:
                for key, value in document.dict().items():
                    if key in self.supported_keys and value:
                        dense_vectors = self.model.encode(value)
                        if len(dense_vectors) > 0:
                            action["_source"][f"{key}_dense_vector"] = dense_vectors
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
