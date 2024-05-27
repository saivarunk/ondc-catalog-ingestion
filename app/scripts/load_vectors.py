import json

import pandas as pd

from tqdm import tqdm
from kafka import KafkaProducer

# Kafka configuration
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic = 'index-products'

# Read the CSV file
csv_file = "app/dataset/BigBasketProducts.csv"
dataset = pd.read_csv(csv_file)

dataset['product'] = dataset['product'].fillna("")
dataset['rating'] = dataset['rating'].fillna(0)
dataset['description'] = dataset['description'].fillna("")
dataset['brand'] = dataset['brand'].fillna("")

documents = dataset.to_dict(orient="records")

producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for document in tqdm(documents):
    producer.send(kafka_topic, value=document)

producer.flush()
print("Documents loaded into Kafka topic successfully")