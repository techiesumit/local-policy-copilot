"""Application settings loaded from environment.

This module defines `Settings`, a thin wrapper around Pydantic's
`BaseSettings` for loading configuration from environment variables and an
optional `.env` file. The `settings` instance is created at import time and
used across the application (see `app.main`).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed application configuration.

    Attributes:
    - `model_provider`: which provider to use ("mock" or "bedrock").
    - `aws_region`: AWS region for Bedrock calls.
    - `bedrock_model_id`: Bedrock model identifier (empty by default).
    - `bedrock_timeout_seconds`: request timeout for Bedrock.
    """

    model_provider: str = "mock"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = ""
    bedrock_timeout_seconds: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
