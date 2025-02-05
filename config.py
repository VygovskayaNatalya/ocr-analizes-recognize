from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "llama3.2"
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1024

    class Config:
        env_file = ".env"

settings = Settings()
