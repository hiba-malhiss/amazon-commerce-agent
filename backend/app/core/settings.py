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
    # Must fit the largest reply prompt: ~600 prompt + the cards (max_cards_per_reply results,
    # ~100 tokens each with their details) + history (max_history_tokens): ~4,500 tokens
    max_response_input_tokens: int = Field(default=12000, gt=0)
    # Must fit the largest Understanding prompt: ~1,000 base + recent requests + the visible
    # results (max_visible_entity_lists x max_cards_per_reply briefs, ~60 tokens each) +
    # history (max_history_tokens): ~6,000 tokens
    max_understanding_input_tokens: int = Field(default=16000, gt=0)
    max_recent_requests: int = Field(default=8, gt=0)
    # Lists of items the user was shown, kept for "the second one" and "the Sony one"
    max_visible_entity_lists: int = Field(default=3, gt=0)
    # Results shown as numbered cards under one reply; the rest aren't shown or sent to it
    max_cards_per_reply: int = Field(default=10, gt=0)

    max_requests_per_turn: int = Field(default=5, gt=0)
    max_parallel_tools: int = Field(default=3, gt=0)
    max_user_message_length: int = Field(default=4000, gt=0)


settings = Settings()
