import os

from app.config.env import get_env
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from env class and .env/.env vars."""
    llm_provider: str = "anthropic"
    llm_api_key: str = ""
    fact_check_api_key: str = ""
    serper_api_key: str = ""
    main_server_secret: str = ""
    ai_mock_llm: bool = False
    rabbitmq_url: str = ""
    log_queue: str = "fakeradar.logs"
    debug: bool = False
    testing: bool = False
    env_name: str = ""

    class Config:
        env_file = ".env"


def build_settings() -> Settings:
    env = get_env()
    mock_raw = os.getenv("AI_MOCK_LLM", "")
    ai_mock_llm = mock_raw.lower() in ("1", "true", "yes") or (
        not env.llm_api_key and mock_raw.lower() != "false"
    )
    return Settings(
        llm_provider=env.llm_provider,
        llm_api_key=env.llm_api_key or "",
        fact_check_api_key=env.fact_check_api_key or "",
        serper_api_key=env.serper_api_key or "",
        main_server_secret=env.main_server_secret,
        ai_mock_llm=ai_mock_llm,
        rabbitmq_url=os.getenv("RABBITMQ_URL", ""),
        log_queue=os.getenv("LOG_QUEUE", "fakeradar.logs"),
        debug=getattr(env, "DEBUG", False),
        testing=getattr(env, "TESTING", False),
        env_name=getattr(env, "ENV_NAME", "")
    )


settings = build_settings()
