from fastapi import FastAPI
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import router as privacy_router
from app.core.database import redis_manager

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Redis Vault...")
    await redis_manager.connect()
    print("Redis Vault connected!")

    yield

    print("Shutting down Redis Vault...")
    await redis_manager.disconnect()
    print("Redis Vault successfully closed.")


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

# include router
app.include_router(privacy_router)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "redis_connected": redis_manager.client is not None,
    }
