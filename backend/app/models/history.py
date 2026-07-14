import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base, pg_enum, GUID


class HistoryAction(str, enum.Enum):
    UPLOAD = "upload"
    ANALYSIS = "analysis"
    CHAT = "chat"
    EXPORT = "export"
    COMPARISON = "comparison"


class HistoryEntry(Base):
    """Audit trail of everything a user has done, shown on the History page."""
    __tablename__ = "history_entries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    project_id = Column(GUID(), ForeignKey("api_projects.id"), nullable=True)

    action = Column(pg_enum(HistoryAction, "historyaction"), nullable=False)
    description = Column(String(1000), nullable=False)
    extra_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="history_entries")
    project = relationship("ApiProject", back_populates="history_entries")
