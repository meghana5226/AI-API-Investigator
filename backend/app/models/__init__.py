"""Import all models here so Alembic's autogenerate and Base.metadata see them."""
from app.models.user import User, UserRole  # noqa
from app.models.api_project import ApiProject, Endpoint, SourceType, ProjectStatus  # noqa
from app.models.chat import ChatSession, ChatMessage, MessageRole  # noqa
from app.models.history import HistoryEntry, HistoryAction  # noqa
