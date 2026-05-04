from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    db_host:     str = "localhost"
    db_port:     int = 5432
    db_name:     str = "marketing_roi_db"
    db_user:     str = "postgres"
    db_password: str = "1410"

    # API
    api_title:   str = "Marketing ROI Dashboard API"
    api_version: str = "1.0.0"
    debug:       bool = True

    # Cache
    cache_ttl:   int = 300

    # 🔥 ADD THESE (AI CONFIG)
    anthropic_api_key: str = ""
    llm_provider: str = "anthropic"
    api_base_url: str = "http://localhost:8000/api/v1"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()