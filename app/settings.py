from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_provider: str = "mock"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = ""
    bedrock_timeout_seconds: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
