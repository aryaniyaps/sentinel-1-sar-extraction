from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sentinel_hub_client_id: str

    sentinel_hub_client_secret: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()  # type: ignore[call-arg]
