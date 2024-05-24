from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ONDC - Catalog Ingestion Service"
    es_host: str = "https://es01:9200"
    es_index: str = "ondc_catlog"
    elastic_username: str
    elastic_password: str
    mongo_host: str = "mongodb"
    mongo_port: int = 27017
    mongo_user: str = "ondc_catlog"
    mongo_password: str = "ondc_catlog"
    mongo_db: str = "ondc_catlog"


settings = Settings()
