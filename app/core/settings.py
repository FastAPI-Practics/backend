from functools import lru_cache

from pydantic import BaseModel, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RBACSettings(BaseModel):
    admin_a: str = 'aa'
    admin_email: EmailStr = 'admin@admin.ru'
    admin_password: str = 'pass'
    admin_role: str = 'admin'
    public_role: str = 'user'


class AuthSettings(BaseModel):
    secret: SecretStr
    algorithm: str = 'HS256'
    access_token_lifetime_seconds: int = 300
    refresh_token_lifetime_seconds: int = 3600


class DbSettings(BaseModel):
    driver: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'pass'
    port: int = 5432
    name: str = 'db'


class Settings(BaseSettings):
    db: DbSettings
    auth: AuthSettings
    rbac: RBACSettings

    model_config = SettingsConfigDict(
        env_file='.env', env_nested_delimiter='__', extra='ignore', case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
