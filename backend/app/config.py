from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    groq_api_key: str = Field(default="")
    llm_primary_model: str = Field(default="llama-3.3-70b-versatile")
    llm_secondary_model: str = Field(default="llama-3.1-8b-instant")
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=4096)

    tavily_api_key: str = Field(default="")
    tavily_max_results: int = Field(default=10)
    tavily_search_depth: str = Field(default="advanced")
    ddg_max_results: int = Field(default=10)

    rss_fetch_timeout_sec: int = Field(default=10)
    rss_max_entries_per_feed: int = Field(default=20)

    scrape_timeout_sec: int = Field(default=15)
    scrape_max_content_length: int = Field(default=5000)
    scrape_user_agent: str = Field(default="MarketMind/1.0 (Research Bot)")

    chroma_persist_dir: str = Field(default="./data/chroma_db")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    rag_chunk_size: int = Field(default=500)
    rag_chunk_overlap: int = Field(default=50)
    rag_top_k: int = Field(default=10)

    database_path: str = Field(default="./data/marketmind.db")
    checkpoint_db_path: str = Field(default="./data/langgraph_checkpoints.db")

    scheduler_enabled: bool = Field(default=True)
    scheduler_default_interval_hours: int = Field(default=24)
    scheduler_max_concurrent_jobs: int = Field(default=2)
    scheduler_jobstore_path: str = Field(default="./data/scheduler_jobs.db")

    groq_primary_rpm: int = Field(default=30)
    groq_secondary_rpm: int = Field(default=30)
    tavily_monthly_limit: int = Field(default=1000)
    tavily_daily_soft_limit: int = Field(default=30)

    report_max_competitors: int = Field(default=5)
    report_max_sources_cited: int = Field(default=15)

    streamlit_port: int = Field(default=8501)

    def resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        return path if path.is_absolute() else BACKEND_DIR / path

    @property
    def database_file(self) -> Path:
        return self.resolve_path(self.database_path)

    @property
    def checkpoint_file(self) -> Path:
        return self.resolve_path(self.checkpoint_db_path)

    @property
    def chroma_dir(self) -> Path:
        return self.resolve_path(self.chroma_persist_dir)

    @property
    def scheduler_jobstore_file(self) -> Path:
        return self.resolve_path(self.scheduler_jobstore_path)

    def ensure_directories(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.database_file.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.scheduler_jobstore_file.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
