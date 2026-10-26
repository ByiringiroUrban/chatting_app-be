import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Muraho Chatting & Business API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-YOUR-ENDPOINT-pooler.region.neon.tech/neondb?sslmode=require",
        description="Neon PostgreSQL connection string"
    )
    
    # Server
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    
    # JWT
    SECRET_KEY: str = "muraho_super_secret_jwt_key_2026_kigali_tech_innovations"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Seed
    AUTO_SEED: bool = True
    
    # SMTP Email Verification
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "urbanpac20@gmail.com"
    SMTP_PASSWORD: str = "lred cuyt impl nahe"
    SMTP_FROM_EMAIL: str = "urbanpac20@gmail.com"
    SMTP_FROM_NAME: str = "Muraho Rwanda"

    # Cloudinary Cloud Storage
    CLOUDINARY_CLOUD_NAME: str = "dyp92boyd"
    CLOUDINARY_API_KEY: str = "226153131222776"
    CLOUDINARY_API_SECRET: str = "aZyk6ueTAQY79YA8MZrpLrgh2b0"

    # Media upload directory (local fallback / temp storage)
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def get_sqlalchemy_database_url(self) -> tuple[str, dict]:
        """
        Parses and prepares the database URL for SQLAlchemy async engine.
        Handles Neon PostgreSQL URLs with SSL and asyncpg driver.
        Falls back to local SQLite if Neon credentials are placeholder or invalid.
        """
        url = self.DATABASE_URL.strip()
        connect_args = {}
        
        # Check if URL is still placeholder
        is_placeholder = (
            "YOUR_NEON_PASSWORD" in url 
            or "YOUR-ENDPOINT" in url 
            or not url
        )
        
        if is_placeholder:
            print("[Muraho DB] Notice: Neon DATABASE_URL is not yet configured or is using placeholder credentials.")
            print("[Muraho DB] Falling back to local SQLite async database (muraho.db) for instant development.")
            print("[Muraho DB] To connect to Neon PostgreSQL, update DATABASE_URL in backend/.env with your Neon connection string.")
            return "sqlite+aiosqlite:///./muraho.db", {"check_same_thread": False}
        
        # Format for asyncpg
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        # Handle Neon SSL requirement for asyncpg
        if "sslmode=" in url:
            # asyncpg accepts ssl in connect_args, not in query string directly
            base_url = url.split("?")[0]
            connect_args = {"ssl": True}
            return base_url, connect_args
        elif "neon.tech" in url:
            connect_args = {"ssl": True}
            return url, connect_args
            
        return url, connect_args

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings()
