import pytest

from app.services import llm_service


@pytest.mark.asyncio
async def test_generate_routes_to_groq_when_configured(monkeypatch):
    monkeypatch.setattr("app.services.llm_service.settings.LLM_PROVIDER", "groq")

    called = {}

    async def fake_groq_generate(prompt, system, temperature):
        called["hit"] = True
        return "groq response"

    monkeypatch.setattr(llm_service, "_groq_generate", fake_groq_generate)

    result = await llm_service.generate("hello")
    assert result == "groq response"
    assert called.get("hit") is True


@pytest.mark.asyncio
async def test_generate_routes_to_ollama_by_default(monkeypatch):
    monkeypatch.setattr("app.services.llm_service.settings.LLM_PROVIDER", "ollama")

    called = {}

    async def fake_ollama_generate(prompt, system, temperature):
        called["hit"] = True
        return "ollama response"

    monkeypatch.setattr(llm_service, "_ollama_generate", fake_ollama_generate)

    result = await llm_service.generate("hello")
    assert result == "ollama response"
    assert called.get("hit") is True


def test_groq_headers_raise_when_api_key_missing(monkeypatch):
    monkeypatch.setattr("app.services.llm_service.settings.GROQ_API_KEY", "")
    with pytest.raises(llm_service.LLMUnavailableError):
        llm_service._groq_headers()


def test_groq_headers_include_bearer_token_when_key_present(monkeypatch):
    monkeypatch.setattr("app.services.llm_service.settings.GROQ_API_KEY", "test-key-123")
    headers = llm_service._groq_headers()
    assert headers["Authorization"] == "Bearer test-key-123"


def test_groq_messages_includes_system_prompt_when_given():
    messages = llm_service._groq_messages("What is this API?", "You are a helpful assistant.")
    assert messages[0] == {"role": "system", "content": "You are a helpful assistant."}
    assert messages[1] == {"role": "user", "content": "What is this API?"}


def test_groq_messages_omits_system_prompt_when_not_given():
    messages = llm_service._groq_messages("What is this API?", None)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
