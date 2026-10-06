from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient

from helpers.config import get_settings
from routes import base, data
from stores.LLMProviderFactory import LLMProviderFactory


async def startup_db_client(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.mongo_conn = AsyncMongoClient(settings.MONGO_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGO_DATABASE]
    
    app.state.llm_provider_factory = LLMProviderFactory(config=settings)
    
    # Generation client
    app.state.generation_client = app.state.llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.state.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID
    )
    
    # Embedding client
    app.state.embedding_client = app.state.llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.state.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_SIZE_ID  
    )


async def shutdown_db_client(app: FastAPI):
    await app.state.mongo_conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)