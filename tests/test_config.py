import os
from unittest.mock import patch


def test_settings_defaults():
    with patch.dict(os.environ, {}, clear=True):
        from importlib import reload
        import app.config
        reload(app.config)
        s = app.config.Settings()
        assert s.llm_provider == "greenpt"
        assert s.greenpt_base_url == "https://api.greenpt.ai/v1"
        assert s.port == 8000


def test_settings_from_env():
    env = {"LLM_PROVIDER": "claude", "ANTHROPIC_API_KEY": "test-key"}
    with patch.dict(os.environ, env, clear=True):
        from importlib import reload
        import app.config
        reload(app.config)
        s = app.config.Settings()
        assert s.llm_provider == "claude"
        assert s.anthropic_api_key == "test-key"
