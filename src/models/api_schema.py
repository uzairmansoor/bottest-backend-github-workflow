from datetime import datetime
from typing import List, Optional

from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

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
from src.models.enums import BillingTierEnum, ReportingConfigurationEnum, RunStatusEnum


class ContactFormRequest(SQLModel):
    first_name: str
    last_name: str
    company_name: str
    business_email: str
    message: str


class NotFoundResponse(JSONResponse):
    def __init__(self, model: SQLModel):
        super().__init__(content={"message": f"Resource {model} not found."}, status_code=404)


class InvalidPermissionsResponse(JSONResponse):
    def __init__(self):
        super().__init__(content={"message": "You do not have permission to perform this action."}, status_code=403)


class PaginationData(SQLModel):
    def __init__(self, items_len: int, limit: int, page: int):
        self.current_page = page
        self.total_items = items_len
        self.total_pages = items_len // limit + 1

        if self.current_page < self.total_pages:
            self.next_page = f"?page={self.current_page + 1}&limit={limit}"

        if self.current_page > 1:
            self.previous_page = f"?page={self.current_page - 1}&limit={limit}"

    current_page: int
    total_pages: int
    total_items: int
    next_page: Optional[str] = None
    previous_page: Optional[str] = None


"""---------- BOT ----------"""


class BotCreateRequest(BotBase):
    pass


class BotUpdateRequest(SQLModel):
    name: Optional[str] = None


class BotReadResponse(BotBase, TimestampModelBase):
    id: str
    query_selector: Optional[str] = None


class ListBotReadResponse(SQLModel):
    data: List[BotReadResponse]
    pagination: PaginationData


"""---------- ENVIRONMENT ----------"""


class EnvironmentCreateRequest(EnvironmentBase):
    pass


class EnvironmentUpdateRequest(SQLModel):
    name: Optional[str] = None
    url: Optional[str] = None


class EnvironmentReadResponse(EnvironmentBase, TimestampModelBase):
    id: str


class ListEnvironmentReadResponse(SQLModel):
    data: List[EnvironmentReadResponse]
    pagination: PaginationData


"""---------- SUITE ----------"""


class SuiteCreateRequest(SuiteBase):
    pass


class SuiteUpdateRequest(SQLModel):
    name: Optional[str] = None
    default_success_criteria: Optional[str] = None
    default_iteration_count: Optional[int] = None
    default_variant_count: Optional[int] = None

    reporting_comparison_configuration: Optional[ReportingConfigurationEnum] = None
    reporting_comparison_suite_run_id: Optional[str] = None
    reporting_comparison_environment_id: Optional[str] = None


class SuiteReadResponse(SuiteBase, TimestampModelBase):
    id: str
    default_success_criteria: str
    default_iteration_count: int
    default_variant_count: int

    reporting_comparison_configuration: ReportingConfigurationEnum
    reporting_comparison_suite_run_id: Optional[str] = None
    reporting_comparison_environment_id: Optional[str] = None


class ListSuiteReadResponse(SQLModel):
    data: List[SuiteReadResponse]
    pagination: PaginationData


"""---------- TEST ----------"""


class TestCreateRequest(TestBase):
    pass


class TestUpdateRequest(SQLModel):
    name: Optional[str] = None

    success_criteria: Optional[str] = None
    use_default_success_criteria: Optional[bool] = None
    iteration_count: Optional[int] = None
    use_default_iteration_count: Optional[bool] = None
    variant_count: Optional[int] = None
    use_default_variant_count: Optional[bool] = None
    full_run_enabled: Optional[bool] = None


class RecentTestRuns(TestRunBase, TimestampModelBase):
    id: str
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None


class TestReadResponse(TestBase, TimestampModelBase):
    id: str
    success_criteria: str
    use_default_success_criteria: bool
    iteration_count: int
    use_default_iteration_count: bool
    variant_count: int
    use_default_variant_count: bool
    full_run_enabled: bool

    recent_test_runs: Optional[List[RecentTestRuns]] = None


class ListTestReadResponse(SQLModel):
    data: List[TestReadResponse]
    pagination: PaginationData


"""---------- VARIANT ----------"""


class VariantCreateRequest(VariantBase):
    pass


class VariantUpdateRequest(SQLModel):
    replay_json: Optional[dict] = None


class VariantReadResponse(VariantBase, TimestampModelBase):
    id: str


class ListVariantReadResponse(SQLModel):
    data: List[VariantReadResponse]
    pagination: PaginationData


"""---------- EVALUATION ----------"""


class EvaluationCreateRequest(EvaluationBase):
    pass


class EvaluationReadResponse(EvaluationBase, TimestampModelBase):
    id: str
    conversation_json: Optional[dict] = None
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_baseline_id: Optional[str] = None

    completed_at: Optional[datetime] = None


"""---------- VARIANT RUN ----------"""


class VariantRunCreateRequest(VariantRunBase):
    pass


class VariantRunReadResponse(VariantRunBase, TimestampModelBase):
    id: str
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    evaluations: List[EvaluationReadResponse]


"""---------- TEST RUN ----------"""


class TestRunCreateRequest(TestRunBase):
    pass


class TestRunReadResponse(TestRunBase, TimestampModelBase):
    id: str
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    variant_runs: List[VariantRunReadResponse]


class ListTestRunReadResponse(SQLModel):
    data: List[TestRunReadResponse]
    pagination: PaginationData


"""---------- SUITE RUN ----------"""


class SuiteRunCreateRequest(SuiteRunBase):
    pass


class ShortenedTestRunReadResponse(TestRunReadResponse):
    variant_runs: None = None


class SuiteRunReadResponse(SuiteRunBase, TimestampModelBase):
    id: str
    status: RunStatusEnum
    status_info: Optional[str] = None
    pass_rate: Optional[float] = None
    average_replayed_elapsed_seconds: Optional[float] = None
    completed_at: Optional[datetime] = None

    test_runs: List[TestRunReadResponse]


class ListSuiteRunReadResponse(SQLModel):
    data: List[SuiteRunReadResponse]
    pagination: PaginationData


"""---------- BASELINE ----------"""


class BaselineCreateRequest(BaselineBase):
    pass


class BaselineUpdateRequest(SQLModel):
    name: Optional[str] = None
    conversation_json: Optional[dict] = None


class BaselineReadResponse(BaselineBase, TimestampModelBase):
    id: str
    name: str


class ListBaselineReadResponse(SQLModel):
    data: List[BaselineReadResponse]
    pagination: PaginationData


"""---------- TRENDING ANALYTICS ----------"""


class TrendingSuccessStatuses(SQLModel):
    name: RunStatusEnum
    data: List[int]


class TrendingSuccess(SQLModel):
    suite_id: str
    suite_name: str
    environment_id: str
    environment_name: str

    suite_run_ids: List[str]
    suite_run_names: List[str]
    timestamps: List[datetime]

    evaluations_performed: List[int]
    test_statuses: List[TrendingSuccessStatuses]
    evaluation_pass_rates: List[float]


class TrendingPerformanceBoxes(SQLModel):
    suite_run_id: str
    suite_run_name: str

    values: List[float]
    outliers: Optional[List[float]] = None


class TrendingPerformance(SQLModel):
    suite_id: str
    suite_name: str
    environment_id: str
    environment_name: str

    boxes: List[TrendingPerformanceBoxes]
    timestamps: List[datetime]


class TrendingUsage(SQLModel):
    suite_id: str
    suite_name: str
    environment_id: str
    environment_name: str

    dates: List[str]
    test_runs: List[int]

    total_used: int
    total_available: int
    billing_tier: BillingTierEnum


""" ---------- REPORT ANALYTICS ---------- """


class ReportTestData(SQLModel):
    test_id: str
    test_name: str
    use_default_success_criteria: bool

    baseline_count: int
    variant_count: int
    iteration_count: int
    evaluation_count: int


class ReportOverviewSection(SQLModel):
    total_test_count: int
    total_variant_count: int
    total_evaluation_count: int

    test_pass_rate: float
    comparison_test_pass_rate: float
    delta_test_pass_rate: float

    evaluation_pass_rate: float
    comparison_evaluation_pass_rate: float
    delta_evaluation_pass_rate: float

    run_statuses: List[RunStatusEnum]
    test_status_counts: List[int]
    comparison_test_status_counts: List[int]
    evaluation_status_counts: List[int]
    comparison_evaluation_status_counts: List[int]


class ReportImprovementTest(SQLModel):
    test_id: str
    test_name: str
    pass_rate: float
    comparison_pass_rate: float


class ReportImprovementSection(SQLModel):
    test_improvements: List[ReportImprovementTest]


class ReportFailureTest(SQLModel):
    test_id: str
    test_name: str
    pass_rate: float
    failure_summary: str
    test_run_id: str


class ReportFailureSection(SQLModel):
    test_failures: List[ReportFailureTest]


class ReportPerformanceTest(SQLModel):
    test_id: str
    test_name: str
    average_run_time: float
    comparison_average_run_time: float
    percent_slower: float

    min_run_time: float
    max_run_time: float


class ReportPerformanceSection(SQLModel):
    average_run_time: float
    comparison_average_run_time: float
    improvement_rate: float

    buckets: List[str]
    values: List[int]
    comparison_values: List[int]

    test_performances: List[ReportPerformanceTest]


class ReportResponse(SQLModel):
    suite_run_id: str
    suite_run_timestamp: datetime
    comparison_run_id: str
    comparison_run_timestamp: datetime
    suite_name: str
    tests: List[ReportTestData]

    overview: ReportOverviewSection
    improvements: ReportImprovementSection
    failures: ReportFailureSection
    performance: ReportPerformanceSection
