import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.v1.projects import _get_owned_project
from app.core.database import get_db
from app.models.user import User
from app.services import vector_store

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.get("/{project_id}")
def semantic_search(
    project_id: uuid.UUID,
    q: str = Query(..., min_length=1, description="Natural language search query"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_project(project_id, current_user, db)
    results = vector_store.semantic_search(str(project_id), q, top_k=top_k)
    return {"query": q, "results": results}
