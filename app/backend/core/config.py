from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    STRATZ_TOKEN: str
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings()