"""
Parses uploaded API artifacts (OpenAPI/Swagger JSON or YAML, Postman
collections, PDF or Markdown documentation) into a normalized list of
endpoint dictionaries that the rest of the system can work with.
"""
import json
import logging
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class ParsedEndpoint(dict):
    """Normalized endpoint shape: method, path, summary, description,
    parameters, request_body, responses, tags, requires_auth."""


def _load_json_or_yaml(file_path: str) -> dict:
    text = Path(file_path).read_text(encoding="utf-8")
    stripped = text.strip()
    if stripped.startswith("{"):
        return json.loads(text)
    return yaml.safe_load(text)


def detect_source_type(filename: str, content_preview: dict | None = None) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".md") or lower.endswith(".markdown"):
        return "markdown"
    if content_preview:
        if "info" in content_preview and ("openapi" in content_preview or "swagger" in content_preview):
            return "openapi" if "openapi" in content_preview else "swagger"
        if "item" in content_preview and "info" in content_preview:
            return "postman"
    return "openapi"


def parse_openapi(file_path: str) -> tuple[list[ParsedEndpoint], dict]:
    """Parses an OpenAPI 3.x or Swagger 2.0 document."""
    spec = _load_json_or_yaml(file_path)
    endpoints: list[ParsedEndpoint] = []

    servers = spec.get("servers", [])
    base_url = servers[0]["url"] if servers else spec.get("host", "")

    security_schemes = (spec.get("components", {}) or {}).get("securitySchemes", {})
    if not security_schemes:
        security_schemes = spec.get("securityDefinitions", {})
    auth_type = next(iter(security_schemes.values()), {}).get("type") if security_schemes else None

    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            if not isinstance(details, dict):
                continue
            endpoints.append(ParsedEndpoint(
                method=method.upper(),
                path=path,
                summary=details.get("summary"),
                description=details.get("description"),
                parameters=details.get("parameters", []),
                request_body=details.get("requestBody") or details.get("consumes"),
                responses=details.get("responses", {}),
                tags=details.get("tags", []),
                requires_auth="required" if details.get("security") or security_schemes else "none",
            ))

    metadata = {
        "base_url": base_url,
        "auth_type": auth_type,
        "title": spec.get("info", {}).get("title", "Untitled API"),
        "description": spec.get("info", {}).get("description", ""),
    }
    return endpoints, metadata


def parse_postman(file_path: str) -> tuple[list[ParsedEndpoint], dict]:
    """Parses a Postman Collection v2.x export."""
    collection = _load_json_or_yaml(file_path)
    endpoints: list[ParsedEndpoint] = []

    def walk(items: list, tags: list[str]):
        for item in items:
            if "item" in item:
                walk(item["item"], tags + [item.get("name", "")])
                continue
            request = item.get("request", {})
            if not request:
                continue
            method = request.get("method", "GET").upper()
            url = request.get("url", {})
            raw_url = url.get("raw", "") if isinstance(url, dict) else str(url)
            path = raw_url.split("?")[0]

            headers = request.get("header", [])
            requires_auth = "required" if request.get("auth") or any(
                h.get("key", "").lower() == "authorization" for h in headers
            ) else "none"

            endpoints.append(ParsedEndpoint(
                method=method,
                path=path,
                summary=item.get("name"),
                description=(request.get("description") if isinstance(request.get("description"), str) else None),
                parameters=(url.get("query", []) if isinstance(url, dict) else []),
                request_body=request.get("body"),
                responses={},
                tags=tags,
                requires_auth=requires_auth,
            ))

    walk(collection.get("item", []), [])

    metadata = {
        "base_url": "",
        "auth_type": collection.get("auth", {}).get("type") if collection.get("auth") else None,
        "title": collection.get("info", {}).get("name", "Untitled Collection"),
        "description": collection.get("info", {}).get("description", ""),
    }
    return endpoints, metadata


def parse_pdf(file_path: str) -> tuple[list[ParsedEndpoint], dict]:
    """Extracts text from PDF documentation. No structured endpoints can be
    guaranteed, so this returns raw text chunks as pseudo-endpoints for the
    RAG pipeline to index, and metadata for the project."""
    reader = PdfReader(file_path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

    endpoints: list[ParsedEndpoint] = []
    for i, chunk in enumerate(_chunk_text(full_text, 1000)):
        endpoints.append(ParsedEndpoint(
            method="DOC",
            path=f"/documentation/section-{i + 1}",
            summary=f"Documentation section {i + 1}",
            description=chunk,
            parameters=[],
            request_body=None,
            responses={},
            tags=["documentation"],
            requires_auth="unknown",
        ))

    metadata = {"base_url": "", "auth_type": None, "title": Path(file_path).stem, "description": ""}
    return endpoints, metadata


def parse_markdown(file_path: str) -> tuple[list[ParsedEndpoint], dict]:
    text = Path(file_path).read_text(encoding="utf-8")
    endpoints: list[ParsedEndpoint] = []
    for i, chunk in enumerate(_chunk_text(text, 1000)):
        endpoints.append(ParsedEndpoint(
            method="DOC",
            path=f"/documentation/section-{i + 1}",
            summary=f"Documentation section {i + 1}",
            description=chunk,
            parameters=[],
            request_body=None,
            responses={},
            tags=["documentation"],
            requires_auth="unknown",
        ))
    metadata = {"base_url": "", "auth_type": None, "title": Path(file_path).stem, "description": ""}
    return endpoints, metadata


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    words = text.split()
    chunks, current = [], []
    current_len = 0
    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current))
            current, current_len = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks or [text]


def parse_file(file_path: str, source_type: str) -> tuple[list[ParsedEndpoint], dict[str, Any]]:
    """Dispatches to the correct parser based on source_type."""
    parsers = {
        "openapi": parse_openapi,
        "swagger": parse_openapi,
        "postman": parse_postman,
        "pdf": parse_pdf,
        "markdown": parse_markdown,
    }
    parser = parsers.get(source_type)
    if parser is None:
        raise ValueError(f"Unsupported source type: {source_type}")
    logger.info("Parsing file %s as %s", file_path, source_type)
    return parser(file_path)
