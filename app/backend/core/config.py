from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    STRATZ_TOKEN: str = ""
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()