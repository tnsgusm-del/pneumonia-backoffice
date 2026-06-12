from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    DB_USER: str = "ozcoding"
    DB_PASSWORD: str = "pw1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3307"
    DB_NAME: str = "ai_health"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()