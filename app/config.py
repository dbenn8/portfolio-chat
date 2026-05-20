from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "openrouter"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    greenpt_api_key: str = ""
    greenpt_base_url: str = "https://api.greenpt.ai/v1"
    greenpt_chat_model: str = "gemma-3-27b-it"
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4-6"
    local_llm_url: str = ""
    local_llm_model: str = "qwen3.5-27b"

    hindsight_url: str = "https://hindsight.applikuapp.com"
    hindsight_api_key: str = ""

    ingest_api_key: str = "change-me"

    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
