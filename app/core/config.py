"""
Core configuration module for Cura Medical AI Assistant
Centralized settings management with validation and environment support
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
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
    mongo_host: str = Field(default="localhost", env="MONGO_HOST")
    mongo_port: int = Field(default=27017, env="MONGO_PORT")
    mongo_database: str = Field(default="cura_medical", env="MONGO_DATABASE")
    mongo_username: Optional[str] = Field(default=None, env="MONGO_USERNAME")
    mongo_password: Optional[str] = Field(default=None, env="MONGO_PASSWORD")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    pdf_dir: Path = Field(default_factory=lambda: Path("data/pdfs"))
    vector_store_path: Path = Field(default_factory=lambda: Path("faiss_index"))
    
    # Features
    enable_voice: bool = Field(default=True, env="ENABLE_VOICE")
    enable_imaging: bool = Field(default=True, env="ENABLE_IMAGING")
    enable_medical_analysis: bool = Field(default=True, env="ENABLE_MEDICAL_ANALYSIS")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], 
        env="CORS_ORIGINS"
    )
    
    # Embedding
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def mongodb_url(self) -> str:
        """Build MongoDB connection URL"""
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