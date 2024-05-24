import pandas as pd
import requests

from tqdm import tqdm

import pandas as pd

backend_host = "http://localhost"

# Read the CSV file
csv_file = "app/dataset/BigBasketProducts.csv"
dataset = pd.read_csv(csv_file)

dataset['product'] = dataset['product'].fillna("")
dataset['rating'] = dataset['rating'].fillna(0)
dataset['description'] = dataset['description'].fillna("")
dataset['brand'] = dataset['brand'].fillna("")

documents = dataset.to_dict(orient="records")
batch_size = 100

for i in tqdm(range(0, len(documents), batch_size)):
    batch = documents[i:i + batch_size]
    response = requests.post(f"{backend_host}/documents/index", json={
        "records": batch,
        "enable_vector_indexing": True
    })
    response.raise_for_status()

print("Data loaded successfully")