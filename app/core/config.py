"""
Core configuration module for Cura Medical AI Assistant
Centralized settings management with validation and environment support
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    app_name: str = "Cura Medical AI Assistant"
    version: str = "3.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # AI Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    llm_model: str = Field(default="gemini-1.5-pro", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    
    # Database
    mongo_uri: Optional[str] = Field(default=None, env="MONGO_URI")
    mongo_host: str = Field(default="localhost", env="MONGO_HOST")
    mongo_port: int = Field(default=27017, env="MONGO_PORT")
    mongo_database: str = Field(default="cura_medical", env="MONGO_DATABASE")
    mongo_username: Optional[str] = Field(default=None, env="MONGO_USERNAME")
    mongo_password: Optional[str] = Field(default=None, env="MONGO_PASSWORD")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    pdf_dir: Path = Field(default_factory=lambda: Path("data/pdfs"))
    upload_dir: Path = Field(default_factory=lambda: Path("data/uploads"))
    vector_store_path: Path = Field(default_factory=lambda: Path("faiss_index"))
    
    # Features
    enable_voice: bool = Field(default=True, env="ENABLE_VOICE")
    enable_imaging: bool = Field(default=True, env="ENABLE_IMAGING")
    enable_medical_analysis: bool = Field(default=True, env="ENABLE_MEDICAL_ANALYSIS")
    enable_symptom_checker: bool = Field(default=True, env="ENABLE_SYMPTOM_CHECKER")
    enable_drug_interactions: bool = Field(default=True, env="ENABLE_DRUG_INTERACTIONS")
    enable_image_analysis: bool = Field(default=False, env="ENABLE_IMAGE_ANALYSIS")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000", 
        env="CORS_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # Compliance
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")
    medical_disclaimer_required: bool = Field(default=True, env="MEDICAL_DISCLAIMER_REQUIRED")
    
    # Email Configuration
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    from_email: str = Field(default="noreply@cura.ai", env="FROM_EMAIL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Embedding
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string to list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins if isinstance(self.cors_origins, list) else []
    
    @property
    def mongodb_url(self) -> str:
        """Build MongoDB connection URL"""
        # Use mongo_uri if provided (for MongoDB Atlas or custom URIs)
        if self.mongo_uri:
            return self.mongo_uri
        
        # Otherwise build from individual components
        if self.mongo_username and self.mongo_password:
            return (f"mongodb://{self.mongo_username}:{self.mongo_password}@"
                   f"{self.mongo_host}:{self.mongo_port}/{self.mongo_database}")
        return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Export settings
__all__ = ["settings", "Settings"]