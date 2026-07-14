import logging
import math
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.api_project import ApiProject, Endpoint, ProjectStatus, SourceType
from app.models.history import HistoryAction, HistoryEntry
from app.models.user import User
from app.schemas.api_project import (
    ComparisonRequest,
    ComparisonResult,
    EndpointOut,
    PaginatedResponse,
    ProjectListItem,
    ProjectOut,
    ProjectUpdate,
)
from app.services import analysis_service, parser_service, vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["API Projects"])

ALLOWED_EXTENSIONS = {".json", ".yaml", ".yml", ".pdf", ".md", ".markdown"}


def _detect_source_type(filename: str) -> SourceType:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return SourceType.PDF
    if lower.endswith(".md") or lower.endswith(".markdown"):
        return SourceType.MARKDOWN
    return SourceType.OPENAPI  # refined after parsing (openapi/swagger/postman)


@router.post("/upload", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def upload_project(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = upload_dir / stored_name
    stored_path.write_bytes(contents)

    project = ApiProject(
        owner_id=current_user.id,
        name=Path(file.filename).stem,
        source_type=_detect_source_type(file.filename),
        source_filename=file.filename,
        raw_file_path=str(stored_path),
        status=ProjectStatus.PROCESSING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    try:
        _process_project(project, db)
    except Exception as exc:
        logger.exception("Failed to process project %s", project.id)
        project.status = ProjectStatus.FAILED
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Could not parse file: {exc}")

    db.add(HistoryEntry(
        user_id=current_user.id,
        project_id=project.id,
        action=HistoryAction.UPLOAD,
        description=f"Uploaded '{file.filename}'",
    ))
    db.commit()
    db.refresh(project)
    return project


def _process_project(project: ApiProject, db: Session) -> None:
    """Parses the raw file, detects the real source type, persists
    endpoints, and indexes them into the vector store."""
    source_hint = project.source_type.value
    if source_hint == "openapi":
        # Refine: could actually be swagger or postman; sniff the JSON.
        try:
            preview = parser_service._load_json_or_yaml(project.raw_file_path)
            detected = parser_service.detect_source_type(project.source_filename, preview)
            project.source_type = SourceType(detected)
            source_hint = detected
        except Exception:
            pass

    endpoints, metadata = parser_service.parse_file(project.raw_file_path, source_hint)

    project.base_url = metadata.get("base_url") or None
    project.auth_type = metadata.get("auth_type") or None
    if metadata.get("title"):
        project.name = metadata["title"]
    if metadata.get("description"):
        project.description = metadata["description"]

    for ep in endpoints:
        db.add(Endpoint(
            project_id=project.id,
            method=ep["method"],
            path=ep["path"],
            summary=ep.get("summary"),
            description=ep.get("description"),
            parameters=ep.get("parameters"),
            request_body=ep.get("request_body"),
            responses=ep.get("responses"),
            tags=ep.get("tags"),
            requires_auth=ep.get("requires_auth"),
        ))

    project.endpoint_count = len(endpoints)
    project.status = ProjectStatus.READY
    db.commit()

    try:
        vector_store.index_endpoints(str(project.id), endpoints)
    except Exception:
        # Semantic search / chat will be degraded until this succeeds, but
        # the upload itself (parsing + persisting endpoints) already worked,
        # so we don't fail the whole request over an indexing hiccup.
        logger.exception("Vector indexing failed for project %s; endpoints were still saved", project.id)


def _get_owned_project(project_id: uuid.UUID, current_user: User, db: Session) -> ApiProject:
    project = db.query(ApiProject).filter(ApiProject.id == project_id, ApiProject.owner_id == current_user.id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("", response_model=PaginatedResponse)
def list_projects(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ApiProject).filter(ApiProject.owner_id == current_user.id)
    if pagination.search:
        query = query.filter(or_(
            ApiProject.name.ilike(f"%{pagination.search}%"),
            ApiProject.description.ilike(f"%{pagination.search}%"),
        ))
    total = query.count()
    items = (
        query.order_by(ApiProject.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
        .all()
    )
    return PaginatedResponse(
        items=[ProjectListItem.model_validate(p) for p in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=max(1, math.ceil(total / pagination.page_size)),
    )


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_owned_project(project_id, current_user, db)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_owned_project(project_id, current_user, db)
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _get_owned_project(project_id, current_user, db)
    vector_store.delete_project_index(str(project.id))
    db.delete(project)
    db.commit()


@router.get("/{project_id}/endpoints", response_model=PaginatedResponse)
def list_endpoints(
    project_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    method: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_project(project_id, current_user, db)
    query = db.query(Endpoint).filter(Endpoint.project_id == project_id)
    if method:
        query = query.filter(Endpoint.method == method.upper())
    if pagination.search:
        query = query.filter(or_(
            Endpoint.path.ilike(f"%{pagination.search}%"),
            Endpoint.summary.ilike(f"%{pagination.search}%"),
        ))
    total = query.count()
    items = query.order_by(Endpoint.path).offset(pagination.offset).limit(pagination.page_size).all()
    return PaginatedResponse(
        items=[EndpointOut.model_validate(e) for e in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=max(1, math.ceil(total / pagination.page_size)),
    )


@router.get("/{project_id}/endpoints/{endpoint_id}", response_model=EndpointOut)
def get_endpoint(
    project_id: uuid.UUID,
    endpoint_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_project(project_id, current_user, db)
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id, Endpoint.project_id == project_id).first()
    if endpoint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")
    return endpoint


@router.post("/{project_id}/endpoints/{endpoint_id}/explain", response_model=EndpointOut)
async def explain_endpoint(
    project_id: uuid.UUID,
    endpoint_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_project(project_id, current_user, db)
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id, Endpoint.project_id == project_id).first()
    if endpoint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")

    ep_dict = {
        "method": endpoint.method, "path": endpoint.path, "summary": endpoint.summary,
        "description": endpoint.description, "parameters": endpoint.parameters, "responses": endpoint.responses,
    }
    endpoint.ai_explanation = await analysis_service.explain_endpoint(ep_dict)
    project = db.query(ApiProject).filter(ApiProject.id == project_id).first()
    endpoint.sample_curl = analysis_service.generate_curl(ep_dict, project.base_url or "")
    endpoint.sample_python = analysis_service.generate_python(ep_dict, project.base_url or "")
    endpoint.sample_javascript = analysis_service.generate_javascript(ep_dict, project.base_url or "")
    db.commit()
    db.refresh(endpoint)
    return endpoint


@router.post("/{project_id}/analyze", response_model=ProjectOut)
async def analyze_project(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _get_owned_project(project_id, current_user, db)
    endpoints = db.query(Endpoint).filter(Endpoint.project_id == project_id).all()
    ep_dicts = [
        {"method": e.method, "path": e.path, "summary": e.summary, "description": e.description,
         "tags": e.tags, "requires_auth": e.requires_auth}
        for e in endpoints
    ]

    project.ai_summary = await analysis_service.summarize_project(project.name, project.description or "", ep_dicts)
    project.risk_report = await analysis_service.detect_risks(ep_dicts)
    db.commit()

    db.add(HistoryEntry(
        user_id=current_user.id, project_id=project.id,
        action=HistoryAction.ANALYSIS, description=f"Ran AI analysis on '{project.name}'",
    ))
    db.commit()
    db.refresh(project)
    return project


@router.post("/compare", response_model=ComparisonResult)
async def compare_projects(payload: ComparisonRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project_a = _get_owned_project(payload.project_id_a, current_user, db)
    project_b = _get_owned_project(payload.project_id_b, current_user, db)

    endpoints_a = db.query(Endpoint).filter(Endpoint.project_id == project_a.id).all()
    endpoints_b = db.query(Endpoint).filter(Endpoint.project_id == project_b.id).all()

    def to_dicts(eps):
        return [{"method": e.method, "path": e.path} for e in eps]

    result = await analysis_service.compare_projects(project_a.name, to_dicts(endpoints_a), project_b.name, to_dicts(endpoints_b))

    db.add(HistoryEntry(
        user_id=current_user.id, project_id=project_a.id,
        action=HistoryAction.COMPARISON, description=f"Compared '{project_a.name}' vs '{project_b.name}'",
    ))
    db.commit()
    return result
