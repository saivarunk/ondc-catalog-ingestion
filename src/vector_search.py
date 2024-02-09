import requests

from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

#model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer('l3cube-pune/indic-sentence-similarity-sbert')

question = "potato chip"
query_vector_product = model.encode(question)

# Set up Elasticsearch client
client = Elasticsearch("https://localhost:9200", verify_certs=False, basic_auth=('elastic', 'pass@123'))

# Function to perform vector search
def vector_search(index_name, query_vector, field):
    script_query = {
        "script_score": {
            "min_score": 1.5,
            "query": {"match_all": {}},
            "script": {
                "source": f"doc['product_dense_vector'].size() == 0 ? 0 : cosineSimilarity(params.query_vector, '{field}_dense_vector') + 1.0",
                "params": {"query_vector": query_vector.tolist()}
            }
        }
    }
    response = client.search(index=index_name, body={"query": script_query})
    return response

index_name = "product_catalog_indic"

# Perform vector search for product attribute
response_product = vector_search(index_name, query_vector_product, "product")
results = response_product['hits']['hits']

for res in results:
    print(res['_source']['product'])
    print(res['_score'])
    print("\n")