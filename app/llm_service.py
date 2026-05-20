from typing import AsyncGenerator
from app.config import settings

VALID_PROVIDERS = {"claude", "openai", "greenpt", "openrouter", "local"}


class LLMService:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.llm_provider
        if self.provider not in VALID_PROVIDERS:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
        self._chat_client = None
        self._init_clients()

    def _init_clients(self):
        if self.provider == "claude":
            import anthropic
            self._chat_client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )
        elif self.provider == "openai":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "greenpt":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(
                api_key=settings.greenpt_api_key,
                base_url=settings.greenpt_base_url,
            )
        elif self.provider == "openrouter":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
        elif self.provider == "local":
            from openai import AsyncOpenAI
            self._chat_client = AsyncOpenAI(
                api_key="not-needed",
                base_url=settings.local_llm_url + "/v1",
            )

    async def chat_stream(
        self, messages: list[dict], system_prompt: str
    ) -> AsyncGenerator[str, None]:
        if self.provider == "claude":
            async with self._chat_client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            model = self._get_chat_model()
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            stream = await self._chat_client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=1024,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    def _get_chat_model(self) -> str:
        if self.provider == "greenpt":
            return settings.greenpt_chat_model
        elif self.provider == "openai":
            return "gpt-4o-mini"
        elif self.provider == "openrouter":
            return settings.openrouter_model
        elif self.provider == "local":
            return settings.local_llm_model
        return "gpt-4o-mini"
