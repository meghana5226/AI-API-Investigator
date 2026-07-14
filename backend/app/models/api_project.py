import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base, pg_enum, GUID


class SourceType(str, enum.Enum):
    OPENAPI = "openapi"
    SWAGGER = "swagger"
    POSTMAN = "postman"
    PDF = "pdf"
    MARKDOWN = "markdown"


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ApiProject(Base):
    """A single uploaded/investigated API (spec, collection, or doc)."""
    __tablename__ = "api_projects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(pg_enum(SourceType, "sourcetype"), nullable=False)
    source_filename = Column(String(500), nullable=False)
    raw_file_path = Column(String(1000), nullable=False)

    status = Column(pg_enum(ProjectStatus, "projectstatus"), default=ProjectStatus.PENDING, nullable=False)
    base_url = Column(String(500), nullable=True)
    auth_type = Column(String(100), nullable=True)
    ai_summary = Column(Text, nullable=True)
    risk_report = Column(JSON, nullable=True)
    endpoint_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    endpoints = relationship("Endpoint", back_populates="project", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="project", cascade="all, delete-orphan")
    history_entries = relationship("HistoryEntry", back_populates="project", cascade="all, delete-orphan")


class Endpoint(Base):
    """A single endpoint extracted from a project's spec/collection."""
    __tablename__ = "endpoints"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("api_projects.id"), nullable=False)

    method = Column(String(10), nullable=False)
    path = Column(String(1000), nullable=False)
    summary = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    responses = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    requires_auth = Column(String(50), nullable=True)

    ai_explanation = Column(Text, nullable=True)
    sample_curl = Column(Text, nullable=True)
    sample_python = Column(Text, nullable=True)
    sample_javascript = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("ApiProject", back_populates="endpoints")
