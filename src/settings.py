from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ONDC - Catalog Ingestion Service"
    es_host: str = "https://es01:9200"
    elastic_username: str
    elastic_password: str
    kafka_bootstrap_servers: str = 'kafka:29092'
    kafka_topic: str = 'index-products'


settings = Settings()
