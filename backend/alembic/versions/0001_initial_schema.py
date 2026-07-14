"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = postgresql.ENUM("user", "admin", name="userrole", create_type=False)
source_type = postgresql.ENUM("openapi", "swagger", "postman", "pdf", "markdown", name="sourcetype", create_type=False)
project_status = postgresql.ENUM("pending", "processing", "ready", "failed", name="projectstatus", create_type=False)
message_role = postgresql.ENUM("user", "assistant", name="messagerole", create_type=False)
history_action = postgresql.ENUM("upload", "analysis", "chat", "export", "comparison", name="historyaction", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    source_type.create(bind, checkfirst=True)
    project_status.create(bind, checkfirst=True)
    message_role.create(bind, checkfirst=True)
    history_action.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("dark_mode", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "api_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("source_filename", sa.String(500), nullable=False),
        sa.Column("raw_file_path", sa.String(1000), nullable=False),
        sa.Column("status", project_status, nullable=False, server_default="pending"),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("auth_type", sa.String(100), nullable=True),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("risk_report", sa.JSON, nullable=True),
        sa.Column("endpoint_count", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "endpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_projects.id"), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("path", sa.String(1000), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parameters", sa.JSON, nullable=True),
        sa.Column("request_body", sa.JSON, nullable=True),
        sa.Column("responses", sa.JSON, nullable=True),
        sa.Column("tags", sa.JSON, nullable=True),
        sa.Column("requires_auth", sa.String(50), nullable=True),
        sa.Column("ai_explanation", sa.Text, nullable=True),
        sa.Column("sample_curl", sa.Text, nullable=True),
        sa.Column("sample_python", sa.Text, nullable=True),
        sa.Column("sample_javascript", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_projects.id"), nullable=False),
        sa.Column("title", sa.String(255), server_default="New Conversation"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id"), nullable=False),
        sa.Column("role", message_role, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "history_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_projects.id"), nullable=True),
        sa.Column("action", history_action, nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("extra_data", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("history_entries")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("endpoints")
    op.drop_table("api_projects")
    op.drop_table("users")

    bind = op.get_bind()
    history_action.drop(bind, checkfirst=True)
    message_role.drop(bind, checkfirst=True)
    project_status.drop(bind, checkfirst=True)
    source_type.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
