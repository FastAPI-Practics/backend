from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='AUTH_',
        env_file='.env',
        extra='ignore',
    )

    secret: str = 'secret'
    token_lifetime_seconds: int = 300
    token_algorithm: str = 'HS256'

class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        extra='ignore',
    )

    protocol: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'pass'
    port: int = 5432
    name: str = 'db'

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
