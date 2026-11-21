# app/config.py — Settings (3.4)
#
# Read from environment variables or a .env file. Only the composition
# root reads Settings; the core never sees configuration.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_timeout_s: float = 30.0
    embedding_model: str = "text-embedding-3-small"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "chunks"

    min_relevance_threshold: float = 0.5
    chunk_size: int = 500

    # 5.4 — durable human-in-the-loop pauses (empty = in-memory checkpointer)
    checkpoint_database_url: str = ""

    # 5.5 — natural-language queries over a relational database.
    # "sqlite:///path.db" or "sqlite:///:memory:" for local runs, a postgresql:// URL in production.
    structured_database_url: str = "sqlite:///:memory:"
    nlq_schema: str = ""

    # 6.1 — share of answers sent to the LLM judge (0.0 to 1.0)
    judge_sample_rate: float = 0.05
