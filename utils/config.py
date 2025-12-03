"""
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Environment: "development" or "production"
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    
    # API Base URL - determined by environment
    API_BASE_URL = (
        "https://pricing-dev.superform.xyz" 
        if ENV == "development" 
        else "https://pricing.superform.xyz"
    )
    
    # RPC URLs (for future direct chain calls if needed)
    ETHEREUM_RPC_URL = os.getenv("ETHEREUM_RPC_URL", "")
    BASE_RPC_URL = os.getenv("BASE_RPC_URL", "")
    
    # Cache TTL in seconds
    CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
    
    # Auto-refresh interval in seconds
    REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "60"))
