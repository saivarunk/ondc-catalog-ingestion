import asyncio
import json

from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI, Depends

from elastic_client import ElasticsearchClient
from models import Product
from settings import settings
from dependencies import get_es_client
from router import router

app = FastAPI(name=settings.app_name)

loop = asyncio.get_event_loop()

consumer = AIOKafkaConsumer(settings.kafka_topic, bootstrap_servers=settings.kafka_bootstrap_servers, loop=loop)


async def consume(client: ElasticsearchClient = Depends(get_es_client)):
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                document = Product(**json.loads(msg.value))
                client.index_documents([document], True)
            except Exception as e:
                print(json.loads(msg.value))
                print("Error processing document:", e)

    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup_event():
    loop.create_task(consume())

@app.on_event("shutdown")
async def shutdown_event():
    await consumer.stop()

app.include_router(router)