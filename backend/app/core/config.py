"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "lumen-hub"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lumen_hub"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Security
    secret_key: str = Field(..., description="Secret key for JWT signing")
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30

    # Keycloak / OIDC
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "lumen-hub"
    keycloak_client_id: str = "lumen-hub-backend"
    keycloak_client_secret: Optional[str] = None
    oidc_issuer_url: Optional[str] = None
    oidc_jwks_url: Optional[str] = None
    oidc_audience: str = "lumen-hub-api"

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    # SMTP
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    smtp_timeout: int = 30
    smtp_sender_email: Optional[str] = None
    smtp_sender_name: str = "Lumen Hub"

    # LLM (optional)
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None

    # Demo mode (localhost only)
    demo_mode: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def effective_oidc_issuer_url(self) -> str:
        return self.oidc_issuer_url or f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    @property
    def effective_oidc_jwks_url(self) -> str:
        return self.oidc_jwks_url or f"{self.effective_oidc_issuer_url}/protocol/openid-connect/certs"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()