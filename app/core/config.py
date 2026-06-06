from pydantic_settings import BaseSettings
from pydantic import computed_field  # 이 import가 꼭 필요합니다!

class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = "password1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "ai_health"

    # 이 부분을 아래와 같이 작성해서 저장하세요!
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()