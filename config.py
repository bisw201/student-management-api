from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    host : str = Field(validation_alias="DB_HOST")
    port : int = Field(default=5432, validation_alias="DB_PORT")
    name : str = Field(validation_alias="DB_NAME")
    user : str = Field(validation_alias="DB_USER")
    password : str = Field(validation_alias="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
