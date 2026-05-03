from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
 
class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Use .env file for local development.
    """
    
    # App Config
    APP_NAME: str = "Dynamic Pricing Intelligence System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Config
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/pricing_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Scraping
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    PROXY_LIST: Optional[List[str]] = None
    
    # ML Models
    MODEL_PATH: str = "./models"
    MLFLOW_TRACKING_URI: str = "./mlruns"
    MODEL_VERSION: str = "production"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    ALERT_EMAIL_FROM: str = "alerts@pricingai.com"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Scraping Schedule (cron expressions)
    SCRAPING_SCHEDULE: str = "0 */4 * * *"  # Every 4 hours
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
 
@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()