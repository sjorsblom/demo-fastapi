from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Differetmix API"
    debug: bool = True
    enviroment: str = "development"
    mongodb_url: str

    model_config = SettingsConfigDict(env_file=".env")
