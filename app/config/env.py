from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()


class BaseEnv:
    """Base environment class. Extend for specific envs."""
    DEBUG: bool = False
    TESTING: bool = False
    ENV_NAME: str = "base"

    def __init__(self):
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")
        self.llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")
        self.fact_check_api_key: Optional[str] = os.getenv(
            "FACT_CHECK_API_KEY")
        self.serper_api_key: Optional[str] = os.getenv("SERPER_API_KEY")
        self.main_server_secret: str = os.getenv("MAIN_SERVER_SECRET", "")


class DevelopmentEnv(BaseEnv):
    DEBUG = True
    ENV_NAME = "development"


class ProductionEnv(BaseEnv):
    ENV_NAME = "production"


class TestingEnv(BaseEnv):
    TESTING = True
    ENV_NAME = "testing"


def get_env() -> BaseEnv:
    env = os.getenv("FAKERADAR_ENV", "development").lower()
    if env == "production":
        return ProductionEnv()
    elif env == "testing":
        return TestingEnv()
    else:
        return DevelopmentEnv()
