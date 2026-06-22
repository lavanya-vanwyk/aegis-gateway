from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Pydantic looks for an environment variable named APP_ENV or target file
    PROJECT_NAME: str = "Aegis Gateway"
    ENVIRONMENT: str = "dev"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    # SecretStr automatically masks sensitive values when printing/logging
    LLM_API_KEY: SecretStr
    # Configuration block for Pydantic Settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
       
settings = Settings()