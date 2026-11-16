"""Knowledge base file management: list, upload, and delete documents, and follow their
indexing live.

No authentication yet: keep this API local (don't expose it publicly) until access
control is added.
"""

import asyncio
import logging
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.knowledge_base.exceptions import KnowledgeBaseError
from app.knowledge_base.schemas import (
    KnowledgeBaseSummary,
    KnowledgeChunkListResponse,
    KnowledgeChunkResponse,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
)
from app.knowledge_base.services.events import listen_document_events
from app.knowledge_base.services.knowledge_base import KnowledgeBaseService, knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge bases"])


@router.get("", response_model=list[KnowledgeBaseSummary])
async def list_knowledge_bases(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[KnowledgeBaseSummary]:
    service = KnowledgeBaseService(session)
    return [
        KnowledgeBaseSummary(code=kb.code, name=kb.name) for kb in service.list_knowledge_bases()
    ]


@router.get("/{kb_code}/documents", response_model=KnowledgeDocumentListResponse)
async def list_documents(
    kb_code: str, session: Annotated[AsyncSession, Depends(get_db)]
) -> KnowledgeDocumentListResponse:
    service = KnowledgeBaseService(session)
    try:
        documents = await service.list_documents(kb_code)
    except KnowledgeBaseError as error:
        raise http_error(error) from error

    return KnowledgeDocumentListResponse(
        documents=[KnowledgeDocumentResponse.model_validate(d) for d in documents]
    )


@router.post("/{kb_code}/documents", response_model=KnowledgeDocumentResponse, status_code=201)
async def upload_document(
    kb_code: str,
    file: UploadFile,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> KnowledgeDocumentResponse:
    """The document comes back `indexing` (or `ready` when the same content is already
    indexed); the Celery worker indexes it and its status updates as it goes."""
    service = KnowledgeBaseService(session)
    try:
        document = await service.upload_document(kb_code, file.filename or "", await file.read())
    except KnowledgeBaseError as error:
        raise http_error(error) from error

    return KnowledgeDocumentResponse.model_validate(document)


@router.get("/{kb_code}/documents/{document_id}/chunks", response_model=KnowledgeChunkListResponse)
async def list_chunks(
    kb_code: str, document_id: UUID, session: Annotated[AsyncSession, Depends(get_db)]
) -> KnowledgeChunkListResponse:
    service = KnowledgeBaseService(session)
    try:
        chunks = await service.list_chunks(kb_code, document_id)
    except KnowledgeBaseError as error:
        raise http_error(error) from error

    return KnowledgeChunkListResponse(
        chunks=[KnowledgeChunkResponse.model_validate(chunk) for chunk in chunks]
    )


@router.delete("/{kb_code}/documents/{document_id}", status_code=204)
async def delete_document(
    kb_code: str, document_id: UUID, session: Annotated[AsyncSession, Depends(get_db)]
) -> Response:
    service = KnowledgeBaseService(session)
    try:
        await service.delete_document(kb_code, document_id)
    except KnowledgeBaseError as error:
        raise http_error(error) from error
    return Response(status_code=204)


@router.websocket("/{kb_code}/documents/events")
async def document_events_websocket(websocket: WebSocket, kb_code: str) -> None:
    """Pushes every change of the knowledge base's documents (DocumentEvent JSON): uploads,
    indexing steps, ready / failed, deletions. Nothing is expected from the page."""
    try:
        knowledge_base(kb_code)
    except KnowledgeBaseError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unknown knowledge base")
        return

    await websocket.accept()
    # schedule continue object task in the event loop => to be executed
    forwarding = asyncio.create_task(forward_document_events(websocket, kb_code))
    try:
        while True:
            await websocket.receive_text()  # incase the UI closed the connection
    except WebSocketDisconnect:
        pass
    finally:
        forwarding.cancel()  # stops the Redis subscription


# listen to event from radis and send them
async def forward_document_events(websocket: WebSocket, kb_code: str) -> None:
    try:
        async for event in listen_document_events(kb_code):
            await websocket.send_text(event)
    except RedisError:
        # The page reconnects (and reloads its list) once Redis is back
        logger.exception("Lost the document events of %s", kb_code)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


def http_error(error: KnowledgeBaseError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=str(error))
