"""Application settings and configuration."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application constants loaded from environment.

    Note: Environment variables take priority over values loaded from a dotenv file.
    """

    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "distributors"

    LOG_LEVEL: str = "INFO"

    SALESFORCE_DOMAIN: str
    SALESFORCE_USERNAME: str
    SALESFORCE_CONSUMER_KEY: SecretStr

    SALESFORCE_KEYSTORE_PATH: str
    SALESFORCE_KEYSTORE_PASSWORD: SecretStr
    SALESFORCE_CERT_ALIAS: str
    SALESFORCE_CERT_PASSWORD: SecretStr


constants = Settings()  # type: ignore
