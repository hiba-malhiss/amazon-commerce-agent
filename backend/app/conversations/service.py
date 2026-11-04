from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.models import Interaction, Message, Thread
from app.conversations.repositories.interaction import InteractionRepository
from app.conversations.repositories.message import MessageRepository
from app.conversations.repositories.thread import ThreadRepository
from app.conversations.schemas.interaction import InteractionResponse
from app.conversations.schemas.message import (
    MessageBody,
    MessageContext,
    MessageResponse,
)
from app.core.settings import settings


class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.threads = ThreadRepository(session)
        self.interactions = InteractionRepository(session)
        self.messages = MessageRepository(session)

    async def get_or_create_thread(
        self,
        thread_id: UUID | None = None,
    ) -> Thread:
        # Create a new thread if no ID is provided
        if thread_id is None:
            thread = await self.threads.create()
            await self.session.commit()
            return thread

        # Retrieve an existing thread
        thread = await self.threads.get_by_id(thread_id)

        if thread is None:
            raise ValueError(f"Thread '{thread_id}' not found")

        return thread

    async def create_interaction(
        self,
        thread_id: UUID,
        user_message: str,
    ) -> tuple[Interaction, Message]:
        # Create interaction and user message
        interaction = await self.interactions.create(thread_id)

        message = await self.messages.create(
            thread_id=thread_id,
            interaction_id=interaction.id,
            role="user",
            content=user_message,
        )

        # Persist the incoming message before graph execution
        await self.session.commit()

        return interaction, message

    async def process_message(
        self,
        graph: Any,
        message: str,
        thread_id: UUID | None = None,
        on_trace: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> InteractionResponse:
        # Resolve or create conversation
        thread = await self.get_or_create_thread(thread_id)

        # Create interaction and persist user message
        interaction, user_message = await self.create_interaction(
            thread_id=thread.id,
            user_message=message,
        )

        # Restore conversation state using thread ID
        config = {
            "configurable": {
                "thread_id": str(thread.id),
            },
            "max_concurrency": settings.max_parallel_tools,
        }

        # Execute LangGraph. Nodes emit their own trace events with get_stream_writer()
        final_state = None
        async for event in graph.astream(
            {
                "messages": [
                    HumanMessage(
                        content=message,
                        id=str(user_message.id),
                    )
                ]
            },
            config=config,
            stream_mode=["custom", "values"],
            version="v2",
            subgraphs=True,  # include events from the tool workflow's nodes
        ):
            # Subgraph states arrive too; only the top-level one is the final state
            if event["type"] == "values" and not event["ns"]:
                final_state = event["data"]

            elif event["type"] == "custom" and on_trace:
                # {"node", "status": started | completed | failed, "data": {...}}
                await on_trace({"interaction_id": str(interaction.id), **event["data"]})

        if final_state is None:
            raise RuntimeError("No final state received")

        last_message = final_state["messages"][-1]
        reply = last_message.content
        assistant_message = await self.messages.create(
            thread_id=thread.id,
            interaction_id=interaction.id,
            role="assistant",
            content=reply,
        )

        await self.session.commit()

        # Return interaction with the persisted user message
        return InteractionResponse(
            thread_id=thread.id,
            interaction_id=interaction.id,
            user_message=MessageResponse(
                context=MessageContext(
                    message_id=user_message.id,
                    interaction_id=interaction.id,
                    thread_id=thread.id,
                    role="user",
                ),
                body=MessageBody(
                    text=user_message.content,
                    entities=user_message.entities,
                ),
            ),
            assistant_message=MessageResponse(
                context=MessageContext(
                    message_id=assistant_message.id,
                    interaction_id=interaction.id,
                    thread_id=thread.id,
                    role="assistant",
                ),
                body=MessageBody(
                    text=assistant_message.content,
                    entities=assistant_message.entities,
                ),
            ),
        )

    async def get_thread_messages(
        self,
        thread_id: UUID,
    ) -> list[Message]:
        # Verify the conversation exists
        thread = await self.threads.get_by_id(thread_id)

        if thread is None:
            raise ValueError(f"Thread '{thread_id}' not found")

        return await self.messages.get_by_thread(thread_id)
