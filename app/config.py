from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "greenpt"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    greenpt_api_key: str = ""
    greenpt_base_url: str = "https://api.greenpt.ai/v1"
    greenpt_chat_model: str = "gemma-3-27b-it"
    greenpt_embedding_model: str = "green-embedding"

    local_llm_url: str = ""
    local_llm_model: str = "qwen3.5-27b"

    weaviate_url: str = ""
    weaviate_api_key: str = ""

    ingest_api_key: str = "change-me"

    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
