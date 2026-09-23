from fastapi import FastAPI
from routes import base, data
from pymongo import AsyncMongoClient
from helpers.config import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.state.settings = settings
    app.state.mongo_conn = AsyncMongoClient(settings.MONGO_URL)
    app.db_client = app.state.mongo_conn[settings.MONGO_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()


app.include_router(base.base_router)
app.include_router(data.data_router)

