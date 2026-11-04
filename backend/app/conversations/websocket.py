from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.conversations.schemas.websocket import WebSocketChatRequest
from app.conversations.service import ConversationService
from app.database.session import AsyncSessionLocal

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            # Receive and validate the user message
            payload = await websocket.receive_json()

            try:
                body = WebSocketChatRequest.model_validate(payload)
            except ValidationError as exc:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid message format",
                        "details": exc.errors(
                            include_context=False,
                            include_input=False,
                        ),  # exclude user message from err
                    }
                )
                continue

            # Process one interaction
            async with AsyncSessionLocal() as session:
                service = ConversationService(session)

                try:
                    result = await service.process_message(
                        graph=websocket.app.state.agent_graph,
                        message=body.message,
                        thread_id=body.thread_id,
                    )

                    await websocket.send_json(
                        {
                            "type": "interaction_completed",
                            "data": result.model_dump(mode="json"),
                        }
                    )

                except ValueError as exc:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": str(exc),
                        }
                    )

    except WebSocketDisconnect:
        pass
