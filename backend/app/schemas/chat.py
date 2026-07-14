import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    project_id: uuid.UUID
    title: Optional[str] = "New Conversation"


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    created_at: datetime


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatSessionDetail(ChatSessionOut):
    messages: list[ChatMessageOut] = []
