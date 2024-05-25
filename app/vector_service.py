import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from app.dependencies import mongo_db

model_name = 'l3cube-pune/indic-sentence-similarity-sbert'
model = SentenceTransformer(model_name)

app = FastAPI(name="vectorization-service", version="0.1.0")

cache_collection = mongo_db["product_vector_cache"]


class VectorizeRequest(BaseModel):
    text: str


@app.router.post("/vectorize")
async def vectorize(body: VectorizeRequest):
    # check for model + body.text in cache
    cached_vector = cache_collection.find_one({"model_name": model_name, "key": body.text})
    if cached_vector:
        print("Cache hit!")
        return cached_vector["vector"]
    else:
        print("Cache miss!")
        vector = model.encode(body.text).tolist()
        vector_dict = {'key': body.text, 'vector': vector, 'model_name': model_name}
        cache_collection.update_one({'model_name': model_name, 'key': body.text}, {'$set': vector_dict}, upsert=True)
        return vector
