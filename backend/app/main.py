"""QuantTrack FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.analytics.router import router as analytics_router
from app.auth.router import router as auth_router
from app.config import settings
from app.database import init_db
from app.logger import logger
from app.ml.router import router as ml_router
from app.middleware.logging import LoggingMiddleware
from app.nlp.router import router as journals_router
from app.trades.router import router as trades_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc, exc_info=True)

    yield

    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title="QuantTrack API",
        description="ML/NLP-powered trading journal and behavioral analytics platform.",
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LoggingMiddleware)

    @app.get("/api/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Welcome to QuantTrack API",
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
        }

    app.include_router(auth_router)
    app.include_router(trades_router)
    app.include_router(analytics_router)
    app.include_router(journals_router)
    app.include_router(ml_router)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning("HTTP error %s: %s %s", exc.status_code, request.url.path, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error for %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "status_code": 422},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning("Value error on %s: %s", request.url.path, str(exc))
        return JSONResponse(status_code=400, content={"detail": str(exc), "status_code": 400})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception for %s", request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
