from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "bet-backend"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bet"

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000,http://localhost:3002,http://localhost:8080"

    cookie_secure: bool = False

    penaltyblog_python: str = ""
    penaltyblog_bridge: str = ""
    soccerdata_python: str = ""
    soccerdata_bridge: str = ""
    oddsharvester_python: str = ""

    model_config = {"env_prefix": "BET_", "env_file": ".env", "extra": "allow"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
