import logging
import os

from cloudwatch import cloudwatch
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = os.environ.get("ENVIRONMENT")
    database_uri: str = os.environ.get("DATABASE_URI")
    jwks_url: str = os.environ.get("JWKS_URL")
    clerk_api_key: str = os.environ.get("CLERK_API_KEY")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY")
    slack_token: str = os.environ.get("SLACK_TOKEN")

    valid_origins: list = [
        "http://localhost:3000",
        "http://localhost",
        "https://bottest.ai",
        "https://bottest-ai-app.vercel.app",
    ]


load_dotenv()
settings = Settings()

logger = logging.getLogger("cloudwatch_logger")
if settings.environment == "production":
    formatter = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")
    handler = cloudwatch.CloudwatchHandler(log_group="cloudwatch_log_group")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
