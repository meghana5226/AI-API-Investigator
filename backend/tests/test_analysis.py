import pytest

from app.services import llm_service
from app.services.analysis_service import detect_risks, explain_endpoint, generate_curl, generate_javascript, generate_python, summarize_project


@pytest.mark.asyncio
async def test_detect_risks_flags_unauthenticated_mutations():
    endpoints = [
        {"method": "POST", "path": "/users", "requires_auth": "none", "description": "Create user", "tags": []},
        {"method": "GET", "path": "/users", "requires_auth": "none", "description": "List users", "tags": []},
    ]
    report = await detect_risks(endpoints)
    assert report["high"] >= 1
    assert any("POST /users" in issue["endpoint"] for issue in report["issues"])


@pytest.mark.asyncio
async def test_detect_risks_flags_missing_docs():
    endpoints = [{"method": "GET", "path": "/ping", "requires_auth": "none", "description": None, "summary": None, "tags": []}]
    report = await detect_risks(endpoints)
    assert report["low"] >= 1


def test_generate_curl_includes_auth_header_when_required():
    endpoint = {"method": "POST", "path": "/items", "requires_auth": "required", "request_body": {}}
    curl = generate_curl(endpoint, base_url="https://api.test.dev")
    assert "Authorization: Bearer" in curl
    assert "https://api.test.dev/items" in curl


def test_generate_python_snippet_valid_syntax():
    endpoint = {"method": "GET", "path": "/items", "requires_auth": "none"}
    code = generate_python(endpoint, base_url="https://api.test.dev")
    compile(code, "<generated>", "exec")


def test_generate_javascript_snippet_contains_fetch():
    endpoint = {"method": "GET", "path": "/items", "requires_auth": "none"}
    code = generate_javascript(endpoint, base_url="https://api.test.dev")
    assert "fetch(" in code


@pytest.mark.asyncio
async def test_summarize_project_uses_cache_on_second_call(monkeypatch):
    """The second call with identical inputs should hit the Redis cache and
    must NOT call the LLM again."""
    store: dict[str, str] = {}
    monkeypatch.setattr("app.services.analysis_service.get_cached_ai_result", lambda kind, payload: store.get(f"{kind}:{payload.get('title')}"))
    monkeypatch.setattr(
        "app.services.analysis_service.set_cached_ai_result",
        lambda kind, payload, result: store.__setitem__(f"{kind}:{payload.get('title')}", result),
    )

    call_count = {"n": 0}

    async def fake_generate(prompt, system=None, temperature=0.3):
        call_count["n"] += 1
        return "A cached-friendly summary."

    monkeypatch.setattr(llm_service, "generate", fake_generate)

    endpoints = [{"method": "GET", "path": "/items", "summary": "list"}]

    first = await summarize_project("Cache Test API", "desc", endpoints)
    second = await summarize_project("Cache Test API", "desc", endpoints)

    assert first == second == "A cached-friendly summary."
    assert call_count["n"] == 1  # LLM only called once; second call was a cache hit


@pytest.mark.asyncio
async def test_summarize_project_different_inputs_bypass_cache(monkeypatch):
    monkeypatch.setattr("app.services.analysis_service.get_cached_ai_result", lambda kind, payload: None)
    monkeypatch.setattr("app.services.analysis_service.set_cached_ai_result", lambda kind, payload, result: None)

    call_count = {"n": 0}

    async def fake_generate(prompt, system=None, temperature=0.3):
        call_count["n"] += 1
        return f"summary #{call_count['n']}"

    monkeypatch.setattr(llm_service, "generate", fake_generate)

    await summarize_project("API One", "desc", [{"method": "GET", "path": "/a"}])
    await summarize_project("API Two", "desc", [{"method": "GET", "path": "/b"}])

    assert call_count["n"] == 2


@pytest.mark.asyncio
async def test_explain_endpoint_uses_cache_on_second_call(monkeypatch):
    store: dict[str, str] = {}
    monkeypatch.setattr("app.services.analysis_service.get_cached_ai_result", lambda kind, payload: store.get(f"{kind}:{payload.get('path')}"))
    monkeypatch.setattr(
        "app.services.analysis_service.set_cached_ai_result",
        lambda kind, payload, result: store.__setitem__(f"{kind}:{payload.get('path')}", result),
    )

    call_count = {"n": 0}

    async def fake_generate(prompt, system=None, temperature=0.3):
        call_count["n"] += 1
        return "This endpoint lists items."

    monkeypatch.setattr(llm_service, "generate", fake_generate)

    endpoint = {"method": "GET", "path": "/items", "summary": "list", "description": None, "parameters": [], "responses": {}}

    first = await explain_endpoint(endpoint)
    second = await explain_endpoint(endpoint)

    assert first == second
    assert call_count["n"] == 1
