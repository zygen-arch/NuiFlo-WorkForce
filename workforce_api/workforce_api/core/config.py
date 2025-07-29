"""Application configuration (Supabase).
"""
from functools import lru_cache
from typing import List, Optional
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
    
    # Supabase Auth Configuration
    supabase_url: str = Field(default="", env="SUPABASE_URL", description="Supabase project URL")
    supabase_anon_key: str = Field(default="", env="SUPABASE_ANON_KEY", description="Supabase anonymous key")
    supabase_service_key: str = Field(default="", env="SUPABASE_SERVICE_KEY", description="Supabase service role key")
    
    # JWT Configuration
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # LLM API Keys for Hybrid System
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Ollama Configuration (local)
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="mistral:7b-instruct", env="OLLAMA_MODEL")
    
    # Hybrid LLM Settings
    default_quality_preference: str = Field(default="balanced", env="DEFAULT_QUALITY_PREFERENCE")  # fast, balanced, premium
    max_budget_per_task: float = Field(default=1.0, env="MAX_BUDGET_PER_TASK")  # Default $1 per task
    
    # App Configuration
    debug: bool = Field(False, env="DEBUG")
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://localhost:3001",
            "https://*.vercel.app",
            "https://*.netlify.app",
            "https://*.lovableproject.com",
            "https://199b6c59-7083-4e1c-9e5e-e73805023c1b.lovableproject.com"
        ], 
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
        # Using psycopg3 for Python 3.13 compatibility
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"

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
    
    @computed_field
    @property
    def auth_enabled(self) -> bool:
        """Check if Supabase authentication is properly configured."""
        return bool(self.supabase_url and self.supabase_anon_key)

@lru_cache()
def get_settings() -> Settings:  # pragma: no cover
    return Settings() 