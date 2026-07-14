"""
AI analysis features that operate over a whole project: summarization,
risk/security detection, missing-documentation detection, and generating
sample requests/code snippets for individual endpoints.
"""
import json
import logging
import re
from typing import Any
from urllib.parse import quote

from app.services import llm_service
from app.services.cache_service import get_cached_ai_result, set_cached_ai_result

logger = logging.getLogger(__name__)


async def summarize_project(title: str, description: str, endpoints: list[dict[str, Any]]) -> str:
    endpoint_list = "\n".join(f"- {e['method']} {e['path']}: {e.get('summary') or 'no summary'}" for e in endpoints[:60])

    # Cache key is derived from the exact content that shapes the summary,
    # so re-running analysis on an unchanged project is instant and free,
    # while any real change (new endpoint, edited description) naturally
    # produces a fresh cache key and a fresh AI call.
    cache_payload = {"title": title, "description": description, "endpoints": endpoint_list}
    cached = get_cached_ai_result("project_summary", cache_payload)
    if cached is not None:
        return cached

    prompt = (
        f"API Title: {title}\nDescription: {description}\n\n"
        f"Endpoints:\n{endpoint_list}\n\n"
        "Write a concise 3-5 sentence summary of what this API does, who it's "
        "likely for, and its overall structure."
    )
    try:
        summary = await llm_service.generate(prompt, system="You are a senior API documentation writer.")
        set_cached_ai_result("project_summary", cache_payload, summary)
        return summary
    except llm_service.LLMUnavailableError:
        # Fallback summaries are never cached: they're not a real AI result,
        # and we want the very next attempt (once Ollama is back) to retry
        # instead of serving a stale "AI is unavailable" message forever.
        return _fallback_summary(title, endpoints)


def _fallback_summary(title: str, endpoints: list[dict[str, Any]]) -> str:
    methods = {}
    for e in endpoints:
        methods[e["method"]] = methods.get(e["method"], 0) + 1
    breakdown = ", ".join(f"{v} {k}" for k, v in methods.items())
    return (
        f"{title} exposes {len(endpoints)} endpoint(s) ({breakdown}). "
        "AI summarization is unavailable right now (Ollama not reachable) — "
        "this is an automatically generated fallback summary."
    )


async def detect_risks(endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    """Rule-based + AI-assisted risk detection. Rule-based checks always run
    so the feature works even if the LLM is offline; the AI adds nuance."""
    issues = []

    for e in endpoints:
        if e.get("requires_auth") in ("none", None) and e["method"] in ("POST", "PUT", "DELETE", "PATCH"):
            issues.append({
                "severity": "high",
                "endpoint": f"{e['method']} {e['path']}",
                "issue": "Mutating endpoint appears to have no authentication requirement.",
            })
        if not e.get("description") and not e.get("summary"):
            issues.append({
                "severity": "low",
                "endpoint": f"{e['method']} {e['path']}",
                "issue": "Missing documentation (no summary or description).",
            })
        if re.search(r"\{?(id|password|token|key)s?\}?", e.get("path", ""), re.IGNORECASE) and "auth" not in (e.get("tags") or []):
            if e.get("requires_auth") == "none":
                issues.append({
                    "severity": "medium",
                    "endpoint": f"{e['method']} {e['path']}",
                    "issue": "Path references a sensitive identifier without explicit auth requirement.",
                })

    severity_order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return {
        "total_issues": len(issues),
        "high": sum(1 for i in issues if i["severity"] == "high"),
        "medium": sum(1 for i in issues if i["severity"] == "medium"),
        "low": sum(1 for i in issues if i["severity"] == "low"),
        "issues": issues[:100],
    }


async def explain_endpoint(endpoint: dict[str, Any]) -> str:
    cache_payload = {
        "method": endpoint["method"],
        "path": endpoint["path"],
        "summary": endpoint.get("summary"),
        "description": endpoint.get("description"),
        "parameters": endpoint.get("parameters"),
        "responses": endpoint.get("responses"),
    }
    cached = get_cached_ai_result("endpoint_explanation", cache_payload)
    if cached is not None:
        return cached

    prompt = (
        f"Explain this API endpoint clearly for a developer integrating with it.\n\n"
        f"Method: {endpoint['method']}\nPath: {endpoint['path']}\n"
        f"Summary: {endpoint.get('summary') or 'none'}\n"
        f"Description: {endpoint.get('description') or 'none'}\n"
        f"Parameters: {json.dumps(endpoint.get('parameters') or [])[:1000]}\n"
        f"Responses: {json.dumps(endpoint.get('responses') or {})[:1000]}\n\n"
        "Explain: (1) what it does, (2) required parameters, (3) expected response, "
        "(4) any auth requirements. Keep it under 150 words."
    )
    try:
        explanation = await llm_service.generate(prompt, system="You are an API documentation expert.")
        set_cached_ai_result("endpoint_explanation", cache_payload, explanation)
        return explanation
    except llm_service.LLMUnavailableError:
        return (
            f"{endpoint['method']} {endpoint['path']} — "
            f"{endpoint.get('summary') or endpoint.get('description') or 'No description available.'} "
            "(AI explanation unavailable — Ollama not reachable.)"
        )


def generate_curl(endpoint: dict[str, Any], base_url: str = "") -> str:
    url = f"{base_url.rstrip('/')}{endpoint['path']}" if base_url else endpoint["path"]
    method = endpoint["method"]
    parts = [f"curl -X {method} \"{url}\""]
    if endpoint.get("requires_auth") == "required":
        parts.append('  -H "Authorization: Bearer YOUR_TOKEN"')
    if method in ("POST", "PUT", "PATCH") and endpoint.get("request_body"):
        parts.append('  -H "Content-Type: application/json"')
        parts.append("  -d '{ \"key\": \"value\" }'")
    return " \\\n".join(parts)


def generate_python(endpoint: dict[str, Any], base_url: str = "") -> str:
    url = f"{base_url.rstrip('/')}{endpoint['path']}" if base_url else endpoint["path"]
    method = endpoint["method"].lower()
    lines = ["import requests", "", f'url = "{url}"']
    headers_needed = endpoint.get("requires_auth") == "required"
    if headers_needed:
        lines.append('headers = {"Authorization": "Bearer YOUR_TOKEN"}')
    if method in ("post", "put", "patch") and endpoint.get("request_body"):
        lines.append('payload = {"key": "value"}')
        call = f'response = requests.{method}(url, json=payload' + (', headers=headers' if headers_needed else '') + ')'
    else:
        call = f'response = requests.{method}(url' + (', headers=headers' if headers_needed else '') + ')'
    lines.append(call)
    lines.append("print(response.status_code, response.json())")
    return "\n".join(lines)


def generate_javascript(endpoint: dict[str, Any], base_url: str = "") -> str:
    url = f"{base_url.rstrip('/')}{endpoint['path']}" if base_url else endpoint["path"]
    method = endpoint["method"].upper()
    headers_needed = endpoint.get("requires_auth") == "required"
    options = [f'method: "{method}"']
    if headers_needed:
        options.append('headers: { "Authorization": "Bearer YOUR_TOKEN", "Content-Type": "application/json" }')
    elif method in ("POST", "PUT", "PATCH"):
        options.append('headers: { "Content-Type": "application/json" }')
    if method in ("POST", "PUT", "PATCH") and endpoint.get("request_body"):
        options.append('body: JSON.stringify({ key: "value" })')
    options_block = ",\n  ".join(options)
    return (
        f'fetch("{url}", {{\n  {options_block}\n}})\n'
        "  .then((res) => res.json())\n"
        "  .then((data) => console.log(data))\n"
        "  .catch((err) => console.error(err));"
    )


async def compare_projects(
    name_a: str, endpoints_a: list[dict[str, Any]], name_b: str, endpoints_b: list[dict[str, Any]]
) -> dict[str, Any]:
    def sig(e):
        return f"{e['method']} {e['path']}"

    set_a = {sig(e) for e in endpoints_a}
    set_b = {sig(e) for e in endpoints_b}

    only_a = sorted(set_a - set_b)
    only_b = sorted(set_b - set_a)
    common = sorted(set_a & set_b)

    prompt = (
        f"Compare two APIs.\n\nAPI A ({name_a}) has {len(endpoints_a)} endpoints.\n"
        f"API B ({name_b}) has {len(endpoints_b)} endpoints.\n"
        f"Endpoints only in A: {only_a[:20]}\nEndpoints only in B: {only_b[:20]}\n"
        f"Shared endpoints: {common[:20]}\n\n"
        "Write a short 3-4 sentence summary of the key structural differences."
    )
    try:
        summary = await llm_service.generate(prompt, system="You are an API architecture reviewer.")
    except llm_service.LLMUnavailableError:
        summary = (
            f"{name_a} has {len(only_a)} unique endpoint(s), {name_b} has {len(only_b)} unique "
            f"endpoint(s), and they share {len(common)} endpoint(s). "
            "(AI comparison summary unavailable — Ollama not reachable.)"
        )

    return {"only_in_a": only_a, "only_in_b": only_b, "common": common, "ai_summary": summary}
