"""
Seeds the database with a demo user and a sample API project so graders /
interviewers can explore the app immediately without uploading a file
themselves.

Run with: python seed.py
"""
import json
import uuid
from pathlib import Path

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.api_project import ApiProject, Endpoint, ProjectStatus, SourceType
from app.models.user import User, UserRole

SAMPLE_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Bookstore API", "description": "A simple demo bookstore API used to seed the app."},
    "servers": [{"url": "https://api.demo-bookstore.dev"}],
    "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}},
    "paths": {
        "/books": {
            "get": {"summary": "List all books", "tags": ["books"], "responses": {"200": {"description": "OK"}}},
            "post": {"summary": "Create a new book", "tags": ["books"], "security": [{"bearerAuth": []}],
                      "requestBody": {"content": {"application/json": {}}}, "responses": {"201": {"description": "Created"}}},
        },
        "/books/{book_id}": {
            "get": {"summary": "Get a book by ID", "tags": ["books"], "responses": {"200": {"description": "OK"}}},
            "delete": {"summary": "Delete a book", "tags": ["books"], "security": [{"bearerAuth": []}],
                       "responses": {"204": {"description": "Deleted"}}},
        },
        "/authors": {
            "get": {"summary": "List all authors", "tags": ["authors"], "responses": {"200": {"description": "OK"}}},
        },
    },
}


def run():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "demo@apiinvestigator.dev").first()
        if existing:
            print("Seed data already exists. Skipping.")
            return

        demo_user = User(
            email="demo@apiinvestigator.dev",
            full_name="Demo User",
            hashed_password=hash_password("DemoPass123!"),
            role=UserRole.USER,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        upload_dir = Path("uploads") / str(demo_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        spec_path = upload_dir / "bookstore-openapi.json"
        spec_path.write_text(json.dumps(SAMPLE_SPEC, indent=2))

        project = ApiProject(
            owner_id=demo_user.id,
            name="Bookstore API",
            description=SAMPLE_SPEC["info"]["description"],
            source_type=SourceType.OPENAPI,
            source_filename="bookstore-openapi.json",
            raw_file_path=str(spec_path),
            status=ProjectStatus.READY,
            base_url=SAMPLE_SPEC["servers"][0]["url"],
            auth_type="http",
            endpoint_count=5,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        endpoints_data = [
            ("GET", "/books", "List all books", "none"),
            ("POST", "/books", "Create a new book", "required"),
            ("GET", "/books/{book_id}", "Get a book by ID", "none"),
            ("DELETE", "/books/{book_id}", "Delete a book", "required"),
            ("GET", "/authors", "List all authors", "none"),
        ]
        for method, path, summary, auth in endpoints_data:
            db.add(Endpoint(
                project_id=project.id, method=method, path=path, summary=summary,
                tags=["books" if "book" in path else "authors"], requires_auth=auth,
            ))
        db.commit()

        print("Seed complete.")
        print("  Demo login: demo@apiinvestigator.dev / DemoPass123!")
    finally:
        db.close()


if __name__ == "__main__":
    run()
