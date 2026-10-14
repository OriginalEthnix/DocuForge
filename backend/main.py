"""
DocuForge AI — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base, run_migrations
from app.utils.logger import logger
from app.api import auth, projects, generation, export, dashboard, files


# Create all tables and run safe column migrations
Base.metadata.create_all(bind=engine)
run_migrations(engine)


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Software Engineering Documentation Generator",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(generation.router, prefix="/api/projects", tags=["AI Generation"])
app.include_router(export.router, prefix="/api/projects", tags=["Export"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(files.router, prefix="/api/projects", tags=["Files"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    logger.info("API docs available at /api/docs")



@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Application shutting down...")


@app.get("/", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    from app.services.s3_service import is_s3_configured
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "s3_configured": is_s3_configured(),
        "s3_bucket": settings.S3_BUCKET_NAME or "Not configured",
        "docs": "/api/docs",
    }
