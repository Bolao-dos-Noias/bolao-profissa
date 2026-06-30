from datetime import datetime, timezone

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-only-change-me-32-bytes-please"
    database_url: str = "sqlite:///./data/bolao.db"
    bolao_deadline_utc: datetime = datetime(2026, 6, 11, 19, 0, tzinfo=timezone.utc)
    football_data_api_key: str = ""
    admin_token: str = ""
    admin_password: str = "admin"
    app_env: str = "dev"


settings = Settings()

