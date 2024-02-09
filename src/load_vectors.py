from collections import defaultdict
from meilisearch import Client
from tqdm import tqdm
import pandas as pd

from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

# Set up Elasticsearch client
client = Elasticsearch("https://localhost:9200", verify_certs=False, basic_auth=('elastic', 'pass@123'))

# Read the CSV file
csv_file = "dataset/BigBasketProducts.csv"
dataset = pd.read_csv(csv_file)

dataset['product'] = dataset['product'].fillna("")
dataset['rating'] = dataset['rating'].fillna(0)
dataset['description'] = dataset['description'].fillna("")
dataset['brand'] = dataset['brand'].fillna("")

documents = dataset.to_dict(orient="records")
document_batches = [documents[i:i + 1000] for i in range(0, len(documents), 1000)]

# Load the pre-trained model
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

print("Model loaded")

def generate_dense_vectors(field, value):
    try:
        supported_keys = ["product", "category", "sub_category", "brand", "description", "type"]
        if field not in supported_keys:
            return []
        return model.encode(value)
    except Exception as e:
        print(f"Error generating dense vectors for {field}: {e}")
        raise e

# Function to patch document with dense vectors
def patch_document_with_dense_vectors(index_name, doc_id):
    # Retrieve existing document from Elasticsearch
    existing_doc = client.get(index=index_name, id=str(doc_id))['_source']
    updated_doc = existing_doc.copy()
    for key, value in existing_doc.items():
        dense_vectors = generate_dense_vectors(key, value)
        if len(dense_vectors) > 0:
            updated_doc[f"{key}_dense_vector"] = dense_vectors
    
    # Update document in Elasticsearch
    client.update(index=index_name, id=doc_id, body={"doc": updated_doc})

# Index name
index_name = "product_catalog"

# Patch documents with dense vectors
for i, document in enumerate(tqdm(documents)):
    doc_id = document['index']
    patch_document_with_dense_vectors(index_name, doc_id)

print("Patch operation completed.")