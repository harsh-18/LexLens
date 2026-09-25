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
    allow_origins=["*"],  # Allow all for hackathon simplicity and local vite port changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
