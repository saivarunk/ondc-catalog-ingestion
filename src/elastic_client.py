class ElasticsearchClient:

    index_name = "product_catalog"

    def __init__(self, index_name, client, model) -> None:
        self.index_name = index_name
        self.client = client
        self.model = model

    def vector_search(self, field, question):
        query_vector_product = self.model.encode(question)
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": f"doc['product_dense_vector'].size() == 0 ? 0 : cosineSimilarity(params.query_vector, '{field}_dense_vector') + 1.0",
                    "params": {"query_vector": query_vector_product.tolist()}
                }
            }
        }
        response = self.client.search(index=self.index_name, body={"query": script_query})
        return response['hits']['hits']
