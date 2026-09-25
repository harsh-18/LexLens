import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.demo_seeder import seed_demo_data

# Import routers
from backend.app.api.auth import router as auth_router
from backend.app.api.documents import router as documents_router
from backend.app.api.analysis import router as analysis_router
from backend.app.api.qa import router as qa_router
from backend.app.api.compare import router as compare_router
from backend.app.api.consultation import router as consultation_router
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.metrics import router as metrics_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LexLens")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing LexLens database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed demo dataset
    db = SessionLocal()
    try:
        seed_demo_data(db)
        logger.info("LexLens demo dataset seeded and ready.")
    except Exception as e:
        logger.warning(f"Demo seeding warning: {e}")
    finally:
        db.close()
        
    yield
    logger.info("LexLens server shutting down.")

app = FastAPI(
    title="LexLens API",
    description="AI-Native Legal Document Intelligence and Navigation Platform",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GZip response compression for maximum network efficiency
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

import time
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Sliding window rate limiter: 120 req / 60 seconds per IP
_rate_limits = defaultdict(list)

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Rate limit check (exclude static frontend assets and health probes)
    path = request.url.path
    if not path.startswith("/assets") and path != "/health" and not path.endswith((".js", ".css", ".ico", ".svg")):
        timestamps = _rate_limits[client_ip]
        _rate_limits[client_ip] = [t for t in timestamps if now - t < 60]
        if len(_rate_limits[client_ip]) >= 120:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again in 60 seconds."},
                headers={"Retry-After": "60"}
            )
        _rate_limits[client_ip].append(now)

    response: Response = await call_next(request)

    # Production Grade Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https:;"
    )
    return response

# Register API Routers
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(documents_router, prefix=api_v1_prefix)
app.include_router(analysis_router, prefix=api_v1_prefix)
app.include_router(qa_router, prefix=api_v1_prefix)
app.include_router(compare_router, prefix=api_v1_prefix)
app.include_router(consultation_router, prefix=api_v1_prefix)
app.include_router(evaluation_router, prefix=api_v1_prefix)
app.include_router(metrics_router, prefix=api_v1_prefix)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LexLens Legal Intelligence Platform",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Mount static frontend files if built dist exists
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
