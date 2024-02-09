import pandas as pd

from tqdm import tqdm
from elasticsearch import Elasticsearch, helpers

import pandas as pd

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

# Index documents
index_name = "product_catalog"

# Generate actions for bulk indexing
actions = [
    {
        "_index": "product_catalog",
        "_id": document['index'],  # Document ID
        "_source": document
    }
    for i, document in enumerate(documents)
]

# Perform bulk indexing
response = helpers.bulk(client, actions)

print(f"Bulk ingestion completed. Indexed {response[0]} documents.")