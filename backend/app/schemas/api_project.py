import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    source_type: str
    source_filename: str
    status: str
    base_url: Optional[str]
    auth_type: Optional[str]
    ai_summary: Optional[str]
    risk_report: Optional[Any]
    endpoint_count: int
    created_at: datetime
    updated_at: datetime


class ProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    source_type: str
    status: str
    endpoint_count: int
    created_at: datetime


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class EndpointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    method: str
    path: str
    summary: Optional[str]
    description: Optional[str]
    parameters: Optional[Any]
    request_body: Optional[Any]
    responses: Optional[Any]
    tags: Optional[Any]
    requires_auth: Optional[str]
    ai_explanation: Optional[str]
    sample_curl: Optional[str]
    sample_python: Optional[str]
    sample_javascript: Optional[str]


class EndpointListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    path: str
    summary: Optional[str]
    tags: Optional[Any]


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class ComparisonRequest(BaseModel):
    project_id_a: uuid.UUID
    project_id_b: uuid.UUID


class ComparisonResult(BaseModel):
    only_in_a: list[str]
    only_in_b: list[str]
    common: list[str]
    ai_summary: str
