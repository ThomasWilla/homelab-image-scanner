from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    dependencytrack_url: AnyHttpUrl = Field(alias="DEPENDENCYTRACK_URL")
    dependencytrack_api_key: str = Field(alias="DEPENDENCYTRACK_API_KEY")
    scan_interval_seconds: int = Field(default=86400, alias="SCAN_INTERVAL_SECONDS")
    state_db_path: Path = Field(default=Path("/data/state/scanner.db"), alias="STATE_DB_PATH")
    output_dir: Path = Field(default=Path("/data/output"), alias="OUTPUT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def dependencytrack_base_url(self) -> str:
        return str(self.dependencytrack_url).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
