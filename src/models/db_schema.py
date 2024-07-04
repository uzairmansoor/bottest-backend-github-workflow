from datetime import datetime
from typing import List, Optional

from sqlmodel import JSON, Column, Field, Relationship

from src.models.base import (
    BaselineBase,
    BotBase,
    EnvironmentBase,
    EvaluationBase,
    SuiteBase,
    SuiteRunBase,
    TestBase,
    TestRunBase,
    TimestampModelBase,
    VariantBase,
    VariantRunBase,
)
from src.models.enums import ReportingConfigurationEnum, RunStatusEnum
from src.utils import generate_id, get_default_success_criteria


class Bot(BotBase, TimestampModelBase, table=True):
    __tablename__ = "bot"
    id: str = Field(primary_key=True, default_factory=generate_id("bot"))

    query_selector: Optional[str] = None

    environments: List["Environment"] = Relationship(back_populates="bot", sa_relationship_kwargs={"cascade": "delete"})
    suites: List["Suite"] = Relationship(back_populates="bot", sa_relationship_kwargs={"cascade": "delete"})


class Environment(EnvironmentBase, TimestampModelBase, table=True):
    __tablename__ = "environment"
    id: str = Field(primary_key=True, default_factory=generate_id("env"))

    bot: Bot = Relationship(back_populates="environments")
    suite_runs: List["SuiteRun"] = Relationship(
        back_populates="environment", sa_relationship_kwargs={"cascade": "delete"}
    )
    test_runs: List["TestRun"] = Relationship(
        back_populates="environment", sa_relationship_kwargs={"cascade": "delete"}
    )


class Suite(SuiteBase, TimestampModelBase, table=True):
    __tablename__ = "suite"
    id: str = Field(primary_key=True, default_factory=generate_id("swt"))

    default_success_criteria: str = Field(default=get_default_success_criteria())
    default_iteration_count: int = Field(default=1)
    default_variant_count: int = Field(default=1)

    reporting_comparison_configuration: ReportingConfigurationEnum = Field(default=ReportingConfigurationEnum.MRSE)
    reporting_comparison_suite_run_id: Optional[str] = None
    reporting_comparison_environment_id: Optional[str] = None

    bot: Bot = Relationship(back_populates="suites")
    suite_runs: List["SuiteRun"] = Relationship(back_populates="suite", sa_relationship_kwargs={"cascade": "delete"})
    tests: List["Test"] = Relationship(back_populates="suite", sa_relationship_kwargs={"cascade": "delete"})


class SuiteRun(SuiteRunBase, TimestampModelBase, table=True):
    __tablename__ = "suite_run"
    id: str = Field(primary_key=True, default_factory=generate_id("srn"))

    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    suite: Suite = Relationship(back_populates="suite_runs")
    environment: Environment = Relationship(back_populates="suite_runs")
    test_runs: List["TestRun"] = Relationship(back_populates="suite_run")


class Test(TestBase, TimestampModelBase, table=True):
    __tablename__ = "test"
    id: str = Field(primary_key=True, default_factory=generate_id("tst"))

    success_criteria: str
    use_default_success_criteria: bool = True
    iteration_count: int
    use_default_iteration_count: bool = True
    variant_count: int
    use_default_variant_count: bool = True

    full_run_enabled: bool = True

    suite: Suite = Relationship(back_populates="tests")
    test_runs: List["TestRun"] = Relationship(back_populates="test", sa_relationship_kwargs={"cascade": "delete"})
    baselines: List["Baseline"] = Relationship(back_populates="test", sa_relationship_kwargs={"cascade": "delete"})
    variants: List["Variant"] = Relationship(back_populates="test", sa_relationship_kwargs={"cascade": "delete"})


class TestRun(TestRunBase, TimestampModelBase, table=True):
    __tablename__ = "test_run"
    id: str = Field(primary_key=True, default_factory=generate_id("trn"))
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    test: Test = Relationship(back_populates="test_runs")
    environment: Environment = Relationship(back_populates="test_runs")
    suite_run: Optional[SuiteRun] = Relationship(back_populates="test_runs")
    variant_runs: List["VariantRun"] = Relationship(
        back_populates="test_run", sa_relationship_kwargs={"cascade": "delete"}
    )


class Baseline(BaselineBase, TimestampModelBase, table=True):
    __tablename__ = "baseline"
    id: str = Field(primary_key=True, default_factory=generate_id("bln"))

    conversation_json: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))

    test: Test = Relationship(back_populates="baselines")


class Variant(VariantBase, TimestampModelBase, table=True):
    __tablename__ = "variant"

    id: str = Field(primary_key=True, default_factory=generate_id("var"))

    test: Test = Relationship(back_populates="variants")
    variant_runs: List["VariantRun"] = Relationship(
        back_populates="variant", sa_relationship_kwargs={"cascade": "delete"}
    )


class VariantRun(VariantRunBase, TimestampModelBase, table=True):
    __tablename__ = "variant_run"

    id: str = Field(primary_key=True, default_factory=generate_id("vrn"))

    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    test_run: TestRun = Relationship(back_populates="variant_runs")
    variant: Variant = Relationship(back_populates="variant_runs")
    evaluations: List["Evaluation"] = Relationship(
        back_populates="variant_run", sa_relationship_kwargs={"cascade": "delete"}
    )


class Evaluation(EvaluationBase, TimestampModelBase, table=True):
    __tablename__ = "evaluation"

    id: str = Field(primary_key=True, default_factory=generate_id("evl"))
    conversation_json: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))

    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_baseline_id: Optional[str] = None
    completed_at: Optional[datetime] = None

    variant_run: VariantRun = Relationship(back_populates="evaluations")
