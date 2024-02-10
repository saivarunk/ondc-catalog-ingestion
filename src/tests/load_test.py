import pandas as pd
from locust import HttpUser, task, between

class loadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.documents = self.read_dataset()

    def read_dataset(self):
        csv_file = "src/dataset/BigBasketProducts.csv"
        dataset = pd.read_csv(csv_file)
        dataset['product'] = dataset['product'].fillna("")
        dataset['rating'] = dataset['rating'].fillna(0)
        dataset['description'] = dataset['description'].fillna("")
        dataset['brand'] = dataset['brand'].fillna("")
        return dataset.to_dict(orient="records")

    @task
    def load_data(self):
        batch_size = 100
        for i in range(0, len(self.documents), batch_size):
            batch = self.documents[i:i + batch_size]
            self.client.post("/documents/index", json={
                "records": batch,
                "enable_vector_indexing": False
            })
