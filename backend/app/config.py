import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "LexLens"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Storage & DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lexlens.db")
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    
    # AI Keys & Models
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    
    # Auth & Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-lexlens-production-key-change-in-prod-789012345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        extra = "allow"

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
