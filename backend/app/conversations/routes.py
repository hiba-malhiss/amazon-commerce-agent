from uuid import uuid4

from fastapi import APIRouter

from app.conversations.schemas import ThreadResponse

router = APIRouter(prefix="/threads", tags=["Threads"])


@router.post("", response_model=ThreadResponse)
async def create_thread() -> ThreadResponse:
    # Generate a unique conversation ID
    return ThreadResponse(thread_id=str(uuid4()))
