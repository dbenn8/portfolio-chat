import pytest
from unittest.mock import patch, AsyncMock, MagicMock


def test_get_provider_claude():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "claude"
        mock_settings.anthropic_api_key = "test"
        mock_settings.greenpt_api_key = ""
        mock_settings.openai_api_key = ""
        svc = LLMService()
        assert svc.provider == "claude"


def test_get_provider_greenpt():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "greenpt"
        mock_settings.greenpt_api_key = "test"
        mock_settings.greenpt_base_url = "https://api.greenpt.ai/v1"
        mock_settings.greenpt_chat_model = "gemma-3-27b-it"
        svc = LLMService()
        assert svc.provider == "greenpt"


def test_get_provider_invalid():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "nonexistent"
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMService()


def test_openrouter_provider():
    from app.llm_service import LLMService
    with patch("app.llm_service.settings") as mock_settings:
        mock_settings.llm_provider = "openrouter"
        mock_settings.openrouter_api_key = "test"
        mock_settings.openrouter_model = "anthropic/claude-sonnet-4-6"
        svc = LLMService()
        assert svc.provider == "openrouter"
