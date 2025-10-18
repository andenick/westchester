"""
Configuration settings for Westchester County Data Platform API

This file contains all configuration variables that can be customized
for different environments (development, production, testing).
"""

import os
from typing import List

# ============================================================================
# Environment Detection
# ============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ============================================================================
# CORS Configuration
# ============================================================================

def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.

    In production, reads from CORS_ORIGINS environment variable.
    In development, uses localhost origins.

    Returns:
        List of allowed origin URLs
    """
    # Always include development origins
    development_origins = [
        "http://localhost:3000",     # React dev server (npm run dev)
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",     # Alternative localhost
        "http://127.0.0.1:5173",     # Alternative localhost
    ]

    # Get production origins from environment variable
    # Format: "https://domain1.com,https://domain2.com"
    cors_env = os.getenv("CORS_ORIGINS", "")
    production_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

    # MANUAL CONFIGURATION (Uncomment and update when deploying):
    # This is a fallback if environment variables are not set
    manual_production_origins = [
        # "https://your-custom-domain.com",           # Your custom domain
        # "https://www.your-custom-domain.com",       # www version
        # "https://your-site.netlify.app",            # Netlify subdomain (auto-generated)
        # "https://westchester-data.netlify.app",     # Example Netlify subdomain
    ]

    # Combine all origins
    all_origins = development_origins.copy()

    # Add production origins if in production environment
    if ENVIRONMENT == "production":
        all_origins.extend(production_origins)
        # If no environment variable is set, use manual configuration
        if not production_origins:
            all_origins.extend(manual_production_origins)

    # Remove empty strings and duplicates
    all_origins = list(set([origin for origin in all_origins if origin]))

    return all_origins


# ============================================================================
# API Configuration
# ============================================================================

API_TITLE = os.getenv("API_TITLE", "Westchester County Data Platform API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DESCRIPTION = "API for accessing Westchester County government data, transit info, and demographics"

# ============================================================================
# Data Configuration
# ============================================================================

# Maximum file size for API responses (in MB)
MAX_RESPONSE_SIZE_MB = int(os.getenv("MAX_RESPONSE_SIZE_MB", "100"))

# Enable data caching
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default

# ============================================================================
# Security Configuration
# ============================================================================

# API rate limiting (if implemented)
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Enable API key authentication (if implemented)
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"

# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

# ============================================================================
# Database Configuration (Future Use)
# ============================================================================

# Uncomment when database is implemented
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./westchester.db")
# DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))

# ============================================================================
# Deployment Information
# ============================================================================

def get_config_summary() -> dict:
    """Return summary of current configuration for debugging"""
    return {
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "api_title": API_TITLE,
        "api_version": API_VERSION,
        "cors_origins": get_cors_origins(),
        "caching_enabled": ENABLE_CACHING,
        "rate_limiting_enabled": RATE_LIMIT_ENABLED,
    }
