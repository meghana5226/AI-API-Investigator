import math

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_current_user
from app.core.database import get_db
from app.models.history import HistoryEntry
from app.models.user import User
from app.schemas.api_project import PaginatedResponse
from app.schemas.history import HistoryEntryOut

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=PaginatedResponse)
def list_history(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(HistoryEntry).filter(HistoryEntry.user_id == current_user.id)
    if pagination.search:
        query = query.filter(HistoryEntry.description.ilike(f"%{pagination.search}%"))
    total = query.count()
    items = query.order_by(HistoryEntry.created_at.desc()).offset(pagination.offset).limit(pagination.page_size).all()
    return PaginatedResponse(
        items=[HistoryEntryOut.model_validate(h) for h in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=max(1, math.ceil(total / pagination.page_size)),
    )
