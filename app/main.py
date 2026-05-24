import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from config import settings
from routes import router

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version="1.0.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_title,
        version="1.0.0",
        description=settings.app_description,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Include routes
app.include_router(router, prefix="/api", tags=["restaurant"])


@app.on_event("startup")
async def startup_event():
    """Log startup"""
    logger.info(f"Starting {settings.app_title}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Models - Creative: {settings.MODEL_CREATIVE}, Structured: {settings.MODEL_STRUCTURED}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info(f"Shutting down {settings.app_title}")


# Root endpoint
@app.get(
    "/",
    summary="API Information",
    tags=["info"]
)
async def root():
    """
    Welcome endpoint with API information
    
    **Navigate to `/docs` for interactive API documentation**
    **Navigate to `/redoc` for ReDoc documentation**
    """
    return {
        "message": "Welcome to Restaurant Idea Generator API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "generate": "POST /api/generate",
            "generate_batch": "POST /api/generate-batch",
            "health": "GET /api/health",
            "examples": "GET /api/examples"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )
