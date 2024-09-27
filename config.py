from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    sentinel_api_username: str

    sentinel_api_password: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()  # type: ignore[call-arg]
