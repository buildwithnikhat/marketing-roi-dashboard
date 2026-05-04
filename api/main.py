# api/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from api.config import get_settings
from api.routers import kpis
from api.models import APIResponse

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Marketing ROI Dashboard API",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_timing(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    ms       = round((time.time()-start)*1000, 2)
    response.headers["X-Process-Time-Ms"] = str(ms)
    return response

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=APIResponse.fail(str(exc)).model_dump()
    )

app.include_router(kpis.router, prefix="/api/v1")

@app.get("/api/v1/health", tags=["System"])
async def health_check():
    return {
        "status":  "healthy",
        "version": settings.api_version,
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Marketing ROI Dashboard API",
        "docs":    "/docs",
        "health":  "/api/v1/health"
    }