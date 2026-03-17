from app.config.env import get_env
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from env class and .env/.env vars."""
    llm_provider: str
    llm_api_key: str
    fact_check_api_key: str
    serper_api_key: str
    main_server_secret: str = ""
    debug: bool = False
    testing: bool = False
    env_name: str = ""

    class Config:
        env_file = ".env"


def build_settings() -> Settings:
    env = get_env()
    return Settings(
        llm_provider=env.llm_provider,
        llm_api_key=env.llm_api_key,
        fact_check_api_key=env.fact_check_api_key,
        serper_api_key=env.serper_api_key,
        main_server_secret=env.main_server_secret,
        debug=getattr(env, "DEBUG", False),
        testing=getattr(env, "TESTING", False),
        env_name=getattr(env, "ENV_NAME", "")
    )


settings = build_settings()
