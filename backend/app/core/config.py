"""
Application Configuration — reads from .env file
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DocuForge AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./docuforge.db"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://docu-forge-nine.vercel.app",
    ]
    CORS_ORIGIN_REGEX: str = r"^https:\/\/.*\.vercel\.app$"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"

    # PlantUML
    PLANTUML_SERVER: str = "https://www.plantuml.com/plantuml"

    # AWS S3
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_PRESIGNED_URL_EXPIRE_SECONDS: int = 900
    MAX_UPLOAD_SIZE_MB: int = 20

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AI_RATE_LIMIT_PER_MINUTE: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
