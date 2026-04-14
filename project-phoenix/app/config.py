from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Noon"
    app_env: str = "development"
    secret_key: str = "change-me-to-a-random-secret-key"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://phoenix:phoenix@localhost:5432/phoenix_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    # JWT Auth
    jwt_secret: str = "change-me-to-a-random-jwt-secret"
    jwt_lifetime_seconds: int = 3600
    jwt_refresh_lifetime_seconds: int = 604800

    # Xendit
    xendit_api_key: str = ""
    xendit_webhook_token: str = ""

    # RajaOngkir
    rajaongkir_api_key: str = ""
    rajaongkir_account_type: str = "pro"

    # Cloudflare R2
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "noon-assets"
    r2_public_url: str = ""

    # Email
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@example.com"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"

    # Sentry
    sentry_dsn: str = ""

    # i18n
    default_language: str = "id"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
