from fastapi import FastAPI
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import router as privacy_router
from app.api.middleware import ASGIAuditMiddleware
from app.core.database import redis_manager
from app.core.logger import audit_logger

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    audit_logger.info("Starting Redis vault...")
    await redis_manager.connect()
    audit_logger.info("Redis Vault connected!")

    yield

    audit_logger.info("Shutting down Redis Vault...")
    await redis_manager.disconnect()
    audit_logger.info("Redis Vault successfully closed.")


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(ASGIAuditMiddleware)
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
