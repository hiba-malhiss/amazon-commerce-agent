from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    openai_api_key: SecretStr = Field(
        validation_alias="OPENAI_API_KEY",
        min_length=1,
    )

    llm_model: str = "gpt-4.1-mini"
    llm_max_output_tokens: int = Field(default=1600, gt=0)
    llm_timeout_seconds: int = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)

    max_history_messages: int = Field(default=8, gt=0)
    max_history_tokens: int = Field(default=2500, gt=0)
    max_response_input_tokens: int = Field(default=8000, gt=0)
    # Must fit the largest Understanding prompt: ~700 base + max_recent_requests x
    # max_entities_per_request entities (~85 tokens each) + the conversation history
    # (max_history_tokens, which includes the latest message). 8 x 10 entities + 2,500
    # history is ~9,900 tokens. Raise it together with those settings
    max_understanding_input_tokens: int = Field(default=12000, gt=0)
    max_recent_requests: int = Field(default=8, gt=0)
    max_entities_per_request: int = Field(default=10, gt=0)  # top results kept for follow-ups

    max_requests_per_turn: int = Field(default=5, gt=0)
    max_parallel_tools: int = Field(default=3, gt=0)
    max_user_message_length: int = Field(default=4000, gt=0)


settings = Settings()
