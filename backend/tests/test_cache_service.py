from app.services.cache_service import build_cache_key, get_cached_ai_result, set_cached_ai_result


def test_build_cache_key_is_deterministic():
    payload = {"title": "My API", "endpoints": "- GET /items"}
    key1 = build_cache_key("project_summary", payload)
    key2 = build_cache_key("project_summary", payload)
    assert key1 == key2


def test_build_cache_key_changes_when_payload_changes():
    key_a = build_cache_key("project_summary", {"title": "A"})
    key_b = build_cache_key("project_summary", {"title": "B"})
    assert key_a != key_b


def test_build_cache_key_is_order_independent_for_dict_keys():
    key1 = build_cache_key("kind", {"a": 1, "b": 2})
    key2 = build_cache_key("kind", {"b": 2, "a": 1})
    assert key1 == key2


def test_get_cached_ai_result_is_none_on_cache_miss(monkeypatch):
    monkeypatch.setattr("app.services.cache_service.cache_get", lambda key: None)
    result = get_cached_ai_result("project_summary", {"title": "X"})
    assert result is None


def test_set_then_get_returns_cached_value(monkeypatch):
    store: dict[str, str] = {}

    def fake_cache_set(key, value, ttl_seconds=3600):
        store[key] = value

    def fake_cache_get(key):
        return store.get(key)

    monkeypatch.setattr("app.services.cache_service.cache_set", fake_cache_set)
    monkeypatch.setattr("app.services.cache_service.cache_get", fake_cache_get)

    payload = {"title": "Bookstore API", "endpoints": "- GET /books"}
    assert get_cached_ai_result("project_summary", payload) is None

    set_cached_ai_result("project_summary", payload, "This API manages books.")

    assert get_cached_ai_result("project_summary", payload) == "This API manages books."


def test_cache_read_failure_fails_open_instead_of_raising(monkeypatch):
    def broken_cache_get(key):
        raise ConnectionError("redis unreachable")

    monkeypatch.setattr("app.services.cache_service.cache_get", broken_cache_get)
    # Should NOT raise -- a Redis outage must never break an AI response.
    result = get_cached_ai_result("project_summary", {"title": "X"})
    assert result is None


def test_cache_write_failure_does_not_raise(monkeypatch):
    def broken_cache_set(key, value, ttl_seconds=3600):
        raise ConnectionError("redis unreachable")

    monkeypatch.setattr("app.services.cache_service.cache_set", broken_cache_set)
    # Should complete silently -- caching is an optimization, not a
    # correctness requirement.
    set_cached_ai_result("project_summary", {"title": "X"}, "some result")
