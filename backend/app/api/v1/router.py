from fastapi import APIRouter

from app.api.v1 import auth, chat, export, history, projects, search, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)
api_router.include_router(history.router)
api_router.include_router(export.router)
