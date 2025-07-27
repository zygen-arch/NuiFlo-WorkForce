"""Application configuration (Supabase).
"""
from functools import lru_cache
from typing import List
import os
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Supabase Database Configuration
    db_user: str = Field(..., env="DB_USER", description="Database user")
    db_password: str = Field(..., env="DB_PASSWORD", description="Database password")
    db_host: str = Field(..., env="DB_HOST", description="Database host")
    db_port: int = Field(5432, env="DB_PORT", description="Database port")
    db_name: str = Field(..., env="DB_NAME", description="Database name")
    
    # Alternative: Full database URL (for Railway, Render, etc.)
    database_url: str = Field(default="", env="DATABASE_URL", description="Full database URL")
    
    # App Configuration
    debug: bool = Field(False, env="DEBUG")
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"], 
        env="CORS_ORIGINS"
    )
    
    # Server Configuration
    port: int = Field(8000, env="PORT")
    host: str = Field("0.0.0.0", env="HOST")

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    @computed_field
    @property
    def supabase_db_url(self) -> str:
        """Construct the database URL from individual components or use DATABASE_URL."""
        # If DATABASE_URL is provided (common in cloud deployments), use it
        if self.database_url:
            return self.database_url
        
        # Otherwise, construct from individual components
        # Password is already URL-encoded in .env file, so use it directly
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"

    @computed_field
    @property 
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @computed_field
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_debug(self) -> bool:
        return bool(self.debug and not self.is_production)

@lru_cache()
def get_settings() -> Settings:  # pragma: no cover
    return Settings() 