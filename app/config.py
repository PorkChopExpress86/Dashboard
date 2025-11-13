from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = Field(default="dev", alias="APP_ENV")
    timezone: str = Field(default="America/New_York", alias="TIMEZONE")
    location_city: str = Field(default="Your City", alias="LOCATION_CITY")
    weather_api_key: str | None = Field(default=None, alias="WEATHER_API_KEY")
    calendar_source: str = Field(default="local_json", alias="CALENDAR_SOURCE")
    weather_lat: float | None = Field(default=None, alias="WEATHER_LAT")
    weather_lon: float | None = Field(default=None, alias="WEATHER_LON")
    google_calendar_ical_url: str | None = Field(default=None, alias="GOOGLE_CALENDAR_ICAL_URL")
    calendar_refresh_minutes: int = Field(default=30, alias="CALENDAR_REFRESH_MINUTES")
    calendar_cache_dir: str = Field(default="./cache", alias="CALENDAR_CACHE_DIR")
    calendar_ical_sources: str | None = Field(default=None, alias="CALENDAR_ICAL_SOURCES")


@lru_cache
def get_settings() -> Settings:
    return Settings()
