from datetime import datetime
from typing import Optional

from sqlmodel import JSON, Column, Field, SQLModel

from src.models.enums import InitiationTypeEnum


class TimestampModelBase(SQLModel):
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_by: str = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class BotBase(SQLModel):
    name: str
    organization_id: Optional[str] = None
    user_id: Optional[str] = None


class EnvironmentBase(SQLModel):
    name: str
    url: str
    bot_id: str = Field(foreign_key="bot.id")


class SuiteBase(SQLModel):
    name: str

    bot_id: str = Field(foreign_key="bot.id")


class SuiteRunBase(SQLModel):
    suite_id: str = Field(foreign_key="suite.id")
    environment_id: str = Field(foreign_key="environment.id")

    initiation_type: InitiationTypeEnum


class TestBase(SQLModel):
    name: str

    suite_id: str = Field(foreign_key="suite.id")


class TestRunBase(SQLModel):
    environment_id: str = Field(foreign_key="environment.id")
    test_id: str = Field(foreign_key="test.id")

    initiation_type: InitiationTypeEnum

    suite_run_id: Optional[str] = Field(default=None, foreign_key="suite_run.id")


class BaselineBase(SQLModel):
    name: str
    html_blob: str
    test_id: str = Field(foreign_key="test.id")

    conversation_json: Optional[dict] = None


class VariantBase(SQLModel):
    test_id: str = Field(foreign_key="test.id")
    replay_json: dict = Field(sa_column=Column(JSON))


class VariantRunBase(SQLModel):
    test_run_id: str = Field(foreign_key="test_run.id")
    variant_id: str = Field(foreign_key="variant.id")

    initiation_type: InitiationTypeEnum


class EvaluationBase(SQLModel):
    variant_run_id: str = Field(foreign_key="variant_run.id")
    html_blob: str
    replayed_elapsed_seconds: float
    initiation_type: InitiationTypeEnum
