from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    google_places_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    database_url: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
