from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.settings import settings


class LLMClient:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            model=settings.llm_model,
            temperature=0,
            max_tokens=settings.llm_max_output_tokens,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )

    async def structured_completion(
        self,
        messages: list[BaseMessage],
        response_schema: type[BaseModel],
    ) -> BaseModel:
        # Generate structured output
        structured_llm = self.llm.with_structured_output(response_schema)

        result = await structured_llm.ainvoke(messages)

        if not isinstance(result, response_schema):
            raise ValueError("Invalid structured LLM response")

        return result


llm_client = LLMClient()
