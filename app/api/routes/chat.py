"""Chat endpoint."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.application.rag.service import RAGService
from app.domain.rag import RAGResponse

router = APIRouter(tags=["chat"])


def _to_response(result: RAGResponse) -> ChatResponse:
    """Convert a domain RAG response to the public API schema."""
    return ChatResponse(
        answer=result.answer,
        sources=[
            {
                "document_id": source.document_id,
                "title": source.title,
                "source": source.source,
            }
            for source in result.sources
        ],
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Answer a user question using the corporate knowledge base."""
    result = rag_service.answer(request.query)
    return _to_response(result)