"""Knowledge base file management: list, upload, and delete documents.

No authentication yet: keep this API local (don't expose it publicly) until access
control is added.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.knowledge_base.exceptions import KnowledgeBaseError
from app.knowledge_base.schemas import (
    KnowledgeBaseSummary,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
)
from app.knowledge_base.services.knowledge_base import KnowledgeBaseService, index_in_background

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
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> KnowledgeDocumentResponse:
    """The document comes back `indexing` (or `ready` when the same content is already
    indexed); it's indexed in the background and its status updates as it goes."""
    service = KnowledgeBaseService(session)
    try:
        document, path = await service.upload_document(
            kb_code, file.filename or "", await file.read()
        )
    except KnowledgeBaseError as error:
        raise http_error(error) from error

    if path is not None:
        background_tasks.add_task(index_in_background, document.id, path, kb_code)
    return KnowledgeDocumentResponse.model_validate(document)


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


def http_error(error: KnowledgeBaseError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=str(error))
