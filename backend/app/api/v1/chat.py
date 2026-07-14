import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.v1.projects import _get_owned_project
from app.core.database import get_db
from app.models.chat import ChatMessage, ChatSession, MessageRole
from app.models.history import HistoryAction, HistoryEntry
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatSessionDetail, ChatSessionOut
from app.services import rag_service

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: ChatSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_owned_project(payload.project_id, current_user, db)
    session = ChatSession(user_id=current_user.id, project_id=payload.project_id, title=payload.title or "New Conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()


def _get_owned_session(session_id: uuid.UUID, current_user: User, db: Session) -> ChatSession:
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_owned_session(session_id, current_user, db)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = _get_owned_session(session_id, current_user, db)
    db.delete(session)
    db.commit()


@router.post("/sessions/{session_id}/messages", response_model=ChatSessionDetail)
async def send_message(
    session_id: uuid.UUID,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Non-streaming endpoint: returns the full session (with the new
    assistant reply appended) in one response. Use /stream for token-by-token."""
    session = _get_owned_session(session_id, current_user, db)

    user_msg = ChatMessage(session_id=session.id, role=MessageRole.USER, content=payload.message)
    db.add(user_msg)
    db.commit()

    history = [{"role": m.role.value, "content": m.content} for m in session.messages]
    answer = await rag_service.answer_question(str(session.project_id), payload.message, history)

    assistant_msg = ChatMessage(session_id=session.id, role=MessageRole.ASSISTANT, content=answer)
    db.add(assistant_msg)

    db.add(HistoryEntry(
        user_id=current_user.id, project_id=session.project_id,
        action=HistoryAction.CHAT, description=f"Asked: '{payload.message[:80]}'",
    ))
    db.commit()
    db.refresh(session)
    return session


@router.post("/sessions/{session_id}/stream")
async def stream_message(
    session_id: uuid.UUID,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Streams the assistant's answer as Server-Sent-Events-style chunks,
    then persists the full exchange once streaming completes."""
    session = _get_owned_session(session_id, current_user, db)

    user_msg = ChatMessage(session_id=session.id, role=MessageRole.USER, content=payload.message)
    db.add(user_msg)
    db.commit()

    history = [{"role": m.role.value, "content": m.content} for m in session.messages]

    async def token_stream():
        collected = []
        async for token in rag_service.stream_answer(str(session.project_id), payload.message, history):
            collected.append(token)
            yield token
        full_answer = "".join(collected)
        assistant_msg = ChatMessage(session_id=session.id, role=MessageRole.ASSISTANT, content=full_answer)
        db.add(assistant_msg)
        db.add(HistoryEntry(
            user_id=current_user.id, project_id=session.project_id,
            action=HistoryAction.CHAT, description=f"Asked: '{payload.message[:80]}'",
        ))
        db.commit()

    return StreamingResponse(token_stream(), media_type="text/plain")
