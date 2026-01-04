from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str
    fdv_ratio_warning_threshold: float = 0.4
    fdv_ratio_target_min: float = 0.45
    fdv_ratio_target_max: float = 0.50
    dev_activity_lookback_days: int = 30
    log_level: str = "INFO"
    http_timeout: int = 30
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
