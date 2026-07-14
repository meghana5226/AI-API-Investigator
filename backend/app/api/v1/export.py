import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.v1.projects import _get_owned_project
from app.core.database import get_db
from app.models.api_project import Endpoint
from app.models.history import HistoryAction, HistoryEntry
from app.models.user import User
from app.services import export_service

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/{project_id}")
def export_report(
    project_id: uuid.UUID,
    format: str = Query("json", pattern="^(json|markdown)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_owned_project(project_id, current_user, db)
    endpoints = db.query(Endpoint).filter(Endpoint.project_id == project_id).all()

    project_dict = {
        "name": project.name, "description": project.description, "source_type": project.source_type.value,
        "base_url": project.base_url, "auth_type": project.auth_type, "ai_summary": project.ai_summary,
        "risk_report": project.risk_report,
    }
    endpoint_dicts = [
        {"method": e.method, "path": e.path, "summary": e.summary, "description": e.description,
         "ai_explanation": e.ai_explanation}
        for e in endpoints
    ]

    db.add(HistoryEntry(
        user_id=current_user.id, project_id=project.id,
        action=HistoryAction.EXPORT, description=f"Exported '{project.name}' as {format}",
    ))
    db.commit()

    if format == "markdown":
        content = export_service.export_as_markdown(project_dict, endpoint_dicts)
        return Response(
            content=content, media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{project.name}-report.md"'},
        )

    content = export_service.export_as_json(project_dict, endpoint_dicts)
    return Response(
        content=content, media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{project.name}-report.json"'},
    )
