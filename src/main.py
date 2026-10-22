from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient

from helpers.config import get_settings
from routes import base, data, nlp
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

async def startup_span(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.mongo_conn = AsyncMongoClient(settings.MONGO_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGO_DATABASE]
    
    # Backward compatibility with routes accessing app.db_client directly
    app.mongo_conn = app.state.mongo_conn
    app.db_client = app.state.db_client
    
    app.state.llm_provider_factory = LLMProviderFactory(config=settings)
    app.state.vectordb_provider_factory = VectorDBProviderFactory(config=settings)
    
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
    
    # Vector store client
    app.state.vectordb_client = app.state.vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.state.vectordb_client.connect()


async def shutdown_span(app: FastAPI):
    await app.state.mongo_conn.close()
    if hasattr(app.state, "vectordb_client") and app.state.vectordb_client:
        app.state.vectordb_client.disconnect()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_span(app)
    yield
    await shutdown_span(app)


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)