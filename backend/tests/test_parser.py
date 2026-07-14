import json

from app.services.parser_service import parse_openapi, parse_postman

SAMPLE_OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "description": "A test API"},
    "servers": [{"url": "https://api.test.dev"}],
    "components": {"securitySchemes": {"bearerAuth": {"type": "http"}}},
    "paths": {
        "/items": {
            "get": {"summary": "List items", "tags": ["items"], "responses": {}},
            "post": {"summary": "Create item", "security": [{"bearerAuth": []}], "responses": {}},
        }
    },
}

SAMPLE_POSTMAN = {
    "info": {"name": "Test Collection", "description": "desc"},
    "item": [
        {
            "name": "Get Items",
            "request": {
                "method": "GET",
                "url": {"raw": "https://api.test.dev/items", "query": []},
                "header": [],
            },
        }
    ],
}


def test_parse_openapi_extracts_endpoints(tmp_path):
    file_path = tmp_path / "spec.json"
    file_path.write_text(json.dumps(SAMPLE_OPENAPI))

    endpoints, metadata = parse_openapi(str(file_path))

    assert len(endpoints) == 2
    assert metadata["title"] == "Test API"
    assert metadata["base_url"] == "https://api.test.dev"

    post_endpoint = next(e for e in endpoints if e["method"] == "POST")
    assert post_endpoint["requires_auth"] == "required"


def test_parse_postman_extracts_endpoints(tmp_path):
    file_path = tmp_path / "collection.json"
    file_path.write_text(json.dumps(SAMPLE_POSTMAN))

    endpoints, metadata = parse_postman(str(file_path))

    assert len(endpoints) == 1
    assert endpoints[0]["method"] == "GET"
    assert endpoints[0]["path"] == "https://api.test.dev/items"
    assert metadata["title"] == "Test Collection"
