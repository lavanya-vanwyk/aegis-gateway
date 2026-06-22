from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import router as privacy_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# include router
app.include_router(privacy_router)

@app.get("/health", tags=["System"])
def health_check():
     return {"status": "healthy",
             "environment": settings.ENVIRONMENT}
