import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('l3cube-pune/indic-sentence-similarity-sbert')

app = FastAPI(name="vectorization-service", version="0.1.0")


class VectorizeRequest(BaseModel):
    text: str


@app.router.post("/vectorize")
async def vectorize(body: VectorizeRequest):
    return model.encode(body.text).tolist()
