"""
The RAG (Retrieval-Augmented Generation) pipeline: retrieve relevant
endpoint chunks from Chroma for a project, then feed them to the LLM
along with conversation history and the user's question.
"""
import logging
from typing import AsyncGenerator

from app.services import llm_service, vector_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert API analyst helping a developer understand an API. "
    "Answer using ONLY the provided endpoint context. If the context doesn't "
    "contain the answer, say so honestly instead of guessing. Be concise and "
    "technical, and reference exact endpoint paths/methods where relevant."
)


def build_context(project_id: str, question: str, top_k: int = 5) -> str:
    hits = vector_store.semantic_search(project_id, question, top_k=top_k)
    if not hits:
        return "No indexed endpoint context is available for this project."
    return "\n\n".join(f"[{h['metadata'].get('method', '')} {h['metadata'].get('path', '')}]\n{h['text']}" for h in hits)


def build_prompt(context: str, history: list[dict], question: str) -> str:
    history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-6:])
    return (
        f"API CONTEXT:\n{context}\n\n"
        f"CONVERSATION HISTORY:\n{history_text}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"ANSWER:"
    )


async def answer_question(project_id: str, question: str, history: list[dict]) -> str:
    context = build_context(project_id, question)
    prompt = build_prompt(context, history, question)
    return await llm_service.generate(prompt, system=SYSTEM_PROMPT)


async def stream_answer(project_id: str, question: str, history: list[dict]) -> AsyncGenerator[str, None]:
    context = build_context(project_id, question)
    prompt = build_prompt(context, history, question)
    async for token in llm_service.stream_generate(prompt, system=SYSTEM_PROMPT):
        yield token
