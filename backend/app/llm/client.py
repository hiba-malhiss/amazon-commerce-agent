from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()

class LLMClient:
    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        temperature: float = 0,
    ):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
        )

    async def structured_completion(
        self,
        messages: list[BaseMessage],
        response_schema: type[BaseModel],
    ) -> Any:
        # Generate and validate structured LLM output
        structured_llm = self.llm.with_structured_output(
            response_schema
        )

        return await structured_llm.ainvoke(messages)


llm_client = LLMClient()
