from datetime import datetime
from random import randrange

from sqlmodel import and_, select
from sqlmodel.orm.session import Session

from src.core.utils import (
    calculate_boxplot_points,
    calculate_performance_buckets,
    has_viewer_permissions,
)
from src.db import with_db_session
from src.models.api_schema import (
    InvalidPermissionsResponse,
    NotFoundResponse,
    ReportFailureSection,
    ReportFailureTest,
    ReportImprovementSection,
    ReportImprovementTest,
    ReportOverviewSection,
    ReportPerformanceSection,
    ReportPerformanceTest,
    ReportResponse,
    ReportTestData,
    TrendingPerformance,
    TrendingPerformanceBoxes,
    TrendingSuccess,
    TrendingSuccessStatuses,
    TrendingUsage,
)
from src.models.db_schema import Environment, Suite, SuiteRun, Test, TestRun
from src.models.enums import BillingTierEnum, ReportingConfigurationEnum, RunStatusEnum


@with_db_session
def get_success_data(suite_id: str, environment_id: str, actor: dict, db_session: Session):
    # get the suite and environment from request
    get_suite = db_session.get(Suite, suite_id)
    get_environment = db_session.get(Environment, environment_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not get_environment:
        return NotFoundResponse(Environment)

    # check if the actor has viewer permissions
    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    # get the past 10 suite runs for the environment
    get_suite_runs = db_session.exec(
        select(SuiteRun)
        .where(and_(SuiteRun.suite_id == suite_id, SuiteRun.environment_id == environment_id))
        .order_by(SuiteRun.created_at.desc())
        .limit(10)
    ).all()

    evaluations_performed = []
    # initialize test statuses (one for each status in enum) with 0s as their data
    test_statuses = [TrendingSuccessStatuses(name=name, data=[0 for _ in range(10)]) for name in RunStatusEnum]
    evaluation_pass_rates = []

    for i, suite_run in enumerate(get_suite_runs):
        # keep track of number of evaluations per suite_run
        evaluation_count = 0
        # keep track of evaluation pass rates
        evaluation_passes = 0

        for test_run in suite_run.test_runs:
            for variant_run in test_run.variant_runs:
                for evaluation in variant_run.evaluations:
                    # increment passes counter
                    if evaluation.status == RunStatusEnum.PASS:
                        evaluation_passes += 1

                # add total number of evaluations
                evaluation_count += len(variant_run.evaluations)

            # in each test run, mark which status it was
            for status in test_statuses:
                if status.name == test_run.status:
                    status.data[i] += 1

        # append the evaluation count for the suite run
        evaluations_performed.append(evaluation_count)
        # append the evaluation pass rates for the suite run
        evaluation_pass_rates.append(evaluation_passes / evaluation_count * 100)

    return TrendingSuccess(
        suite_id=suite_id,
        suite_name=get_suite.name,
        environment_id=environment_id,
        environment_name=get_environment.name,
        suite_run_ids=[suite_run.id for suite_run in get_suite_runs],
        suite_run_names=[suite_run.created_at.strftime("%Y-%m-%d %H:%M:%S") for suite_run in get_suite_runs],
        evaluations_performed=evaluations_performed,
        test_statuses=test_statuses,
        evaluation_pass_rates=evaluation_pass_rates,
        timestamps=[suite_run.created_at for suite_run in get_suite_runs],
    )


@with_db_session
def get_performance_data(suite_id: str, environment_id: str, actor: dict, db_session: Session):
    # get the suite and environment from request
    get_suite = db_session.get(Suite, suite_id)
    get_environment = db_session.get(Environment, environment_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not get_environment:
        return NotFoundResponse(Environment)

    # check if the actor has viewer permissions
    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    # get the past 10 suite runs for the environment
    get_suite_runs = db_session.exec(
        select(SuiteRun)
        .where(and_(SuiteRun.suite_id == suite_id, SuiteRun.environment_id == environment_id))
        .order_by(SuiteRun.created_at.desc())
        .limit(10)
    ).all()

    performance_boxes = []

    for suite_run in get_suite_runs:
        # store all runtimes
        suite_runtimes = []
        for test_run in suite_run.test_runs:
            for variant_run in test_run.variant_runs:
                for evaluation in variant_run.evaluations:
                    # append elapsed time for each evaluation
                    suite_runtimes.append(evaluation.replayed_elapsed_seconds)

        # calculate boxplot points
        values, outliers = calculate_boxplot_points(suite_runtimes)

        # TODO: REMOVE THIS HARDCODING
        if len(outliers) == 0:
            from random import randint

            outliers = [max(values[0] - randint(10, 50), 5)]
            if randint(0, 100) > 50:
                outliers.append(values[-1] + randint(10, 50))
                if randint(0, 100) > 50:
                    outliers.append(values[-1] + randint(10, 50))

        performance_boxes.append(
            TrendingPerformanceBoxes(
                suite_run_id=suite_run.id,
                suite_run_name=suite_run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                values=values,
                outliers=outliers,
            )
        )

    return TrendingPerformance(
        suite_id=suite_id,
        suite_name=get_suite.name,
        environment_id=environment_id,
        environment_name=get_environment.name,
        boxes=performance_boxes,
        timestamps=[suite_run.created_at for suite_run in get_suite_runs],
    )


@with_db_session
def get_usage_data(suite_id: str, environment_id: str, actor: dict, db_session: Session):
    # get the suite and environment from request
    get_suite = db_session.get(Suite, suite_id)
    get_environment = db_session.get(Environment, environment_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not get_environment:
        return NotFoundResponse(Environment)

    # check if the actor has viewer permissions
    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    # get test runs for the environment + suite in past month
    first_day_current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    get_test_ids_for_suite = db_session.exec(select(Test).where(Test.suite_id == suite_id)).all()
    get_test_runs = db_session.exec(
        select(TestRun)
        .where(
            and_(
                TestRun.test_id.in_([test.id for test in get_test_ids_for_suite]),
                TestRun.environment_id == environment_id,
                TestRun.created_at >= first_day_current_month,
            )
        )
        .order_by(TestRun.created_at.desc())
    ).all()

    # track number of test_runs per day
    date_to_test_runs = {}
    for test_run in get_test_runs:
        date = test_run.created_at.strftime("%Y-%m-%d")
        if date not in date_to_test_runs:
            date_to_test_runs[date] = 1
        else:
            date_to_test_runs[date] += 1

    return TrendingUsage(
        suite_id=suite_id,
        suite_name=get_suite.name,
        environment_id=environment_id,
        environment_name=get_environment.name,
        dates=list(date_to_test_runs.keys()),
        test_runs=list(date_to_test_runs.values()),
        total_used=randrange(100, 900),  # TODO: Change this
        total_available=1000,  # TODO: Change this
        billing_tier=BillingTierEnum.FREE,  # TODO: Change this once implement billing tiers
    )


@with_db_session
def get_report_data(suite_run_id: str, actor: dict, db_session: Session):
    # get the suite run from request
    get_suite_run = db_session.get(SuiteRun, suite_run_id)

    if not get_suite_run:
        return NotFoundResponse(SuiteRun)

    get_suite: Suite = get_suite_run.suite

    # check if actor has viewer permissions
    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    # get the comparison run
    reporting_comparison_configuration = get_suite.reporting_comparison_configuration

    # most recent same environment
    if reporting_comparison_configuration == ReportingConfigurationEnum.MRSE:
        get_comparison_run = db_session.exec(
            select(SuiteRun)
            .where(
                and_(
                    SuiteRun.suite_id == get_suite.id,
                    SuiteRun.environment_id == get_suite_run.environment_id,
                    SuiteRun.id != get_suite_run.id,
                )
            )
            .order_by(SuiteRun.created_at.desc())
        ).first()

    # most recent different environment
    elif reporting_comparison_configuration == ReportingConfigurationEnum.MRDE:
        get_comparison_run = db_session.exec(
            select(SuiteRun)
            .where(
                and_(
                    SuiteRun.suite_id == get_suite.id,
                    SuiteRun.environment_id == get_suite.reporting_comparison_environment_id,
                )
            )
            .order_by(SuiteRun.created_at.desc())
        ).first()

    # specific suite run
    elif reporting_comparison_configuration == ReportingConfigurationEnum.SSR:
        get_comparison_run = db_session.get(SuiteRun, get_suite.reporting_comparison_suite_run_id)

    else:
        raise Exception("reporting_comparison_configuration not implemented")

    # store list of run statuses
    status_enum_values = [status.value for status in RunStatusEnum]

    """ ----------------- COMPARISON SECTION -----------------"""

    # store the status counts for comparison run
    comparison_test_status_counts = [0 for _ in status_enum_values]
    comparison_evaluation_status_counts = [0 for _ in status_enum_values]

    # store the comparison tests to pass rate
    comparison_test_id_to_pass_rate = {}

    # store the comparison tests to runtime
    comparison_test_id_to_runtime = {}

    # store the runtimes for evals
    comparison_evaluation_runtimes = []

    # iterate through all test_runs in the comparison run
    for test_run in get_comparison_run.test_runs:
        # store comparison test to pass rate and runtime
        comparison_test_id_to_pass_rate[test_run.test_id] = test_run.pass_rate
        comparison_test_id_to_runtime[test_run.test_id] = test_run.average_replayed_elapsed_seconds

        # increment the status count for corresponding status
        comparison_test_status_counts[status_enum_values.index(test_run.status)] += 1

        for variant_run in test_run.variant_runs:
            for evaluation in variant_run.evaluations:
                # append runtime for evaluation
                comparison_evaluation_runtimes.append(evaluation.replayed_elapsed_seconds)

                # increment the status count for corresponding status
                comparison_evaluation_status_counts[status_enum_values.index(evaluation.status)] += 1

    """ ----------------- MAIN SUITE RUN SECTION -----------------"""

    # track total values
    total_test_count = 0
    total_variant_count = 0
    total_evaluation_count = 0

    # store the test data for first section
    tests_list = []

    # store the test improvements
    test_improvements = []

    # store the test failures
    test_failures = []

    # test and evaluation statuses and their counts
    test_status_counts = [0 for _ in status_enum_values]
    evaluation_status_counts = [0 for _ in status_enum_values]

    # store the runtime for evals
    evaluation_runtimes = []

    # store the tests with worse performance
    test_worst_performance = []

    # iterate through all test runs in suite run
    for test_run in get_suite_run.test_runs:
        test: Test = test_run.test
        baseline_count = len(test.baselines)
        variant_count = len(test.variants)
        evaluation_count = test.iteration_count * variant_count

        # increment total values
        total_test_count += 1
        total_variant_count += variant_count
        total_evaluation_count += evaluation_count

        # append test
        tests_list.append(
            ReportTestData(
                test_id=test.id,
                test_name=test.name,
                use_default_success_criteria=test.use_default_success_criteria,
                baseline_count=baseline_count,
                variant_count=variant_count,
                iteration_count=test.iteration_count,
                evaluation_count=evaluation_count,
            )
        )

        # check if test has improved pass rate
        if test.id in comparison_test_id_to_pass_rate and test_run.pass_rate > comparison_test_id_to_pass_rate[test.id]:
            test_improvements.append(
                ReportImprovementTest(
                    test_id=test.id,
                    test_name=test.name,
                    pass_rate=test_run.pass_rate,
                    comparison_pass_rate=comparison_test_id_to_pass_rate[test.id],
                )
            )

        # increment the status count for corresponding status
        test_status_counts[status_enum_values.index(test_run.status)] += 1

        # if the status is fail or mixed, append to failure details
        if test_run.status in [RunStatusEnum.FAIL, RunStatusEnum.MIXED]:
            test_failures.append(
                ReportFailureTest(
                    test_id=test.id,
                    test_name=test.name,
                    pass_rate=test_run.pass_rate,
                    failure_summary=test_run.status_info,
                    test_run_id=test_run.id,
                )
            )

        # check if runtime was >10% worse than comparison
        if (
            test.id in comparison_test_id_to_runtime
            and test_run.average_replayed_elapsed_seconds > comparison_test_id_to_runtime[test.id] * 1.1
        ):
            # store all runtimes for this test
            runtimes = []
            for variant_run in test_run.variant_runs:
                for evaluation in variant_run.evaluations:
                    runtimes.append(evaluation.replayed_elapsed_seconds)

            test_worst_performance.append(
                ReportPerformanceTest(
                    test_id=test.id,
                    test_name=test.name,
                    average_run_time=test_run.average_replayed_elapsed_seconds,
                    comparison_average_run_time=comparison_test_id_to_runtime[test.id],
                    percent_slower=(
                        test_run.average_replayed_elapsed_seconds / comparison_test_id_to_runtime[test.id] - 1
                    ),
                    min_run_time=min(runtimes),
                    max_run_time=max(runtimes),
                )
            )

        # iterate through all variant runs
        for variant_run in test_run.variant_runs:
            # iterate through all evaluations
            for evaluation in variant_run.evaluations:
                # append runtime for evaluation
                evaluation_runtimes.append(evaluation.replayed_elapsed_seconds)

                # increment the status count for corresponding status
                evaluation_status_counts[status_enum_values.index(evaluation.status)] += 1

    # calculate pass rates for overview section
    test_pass_rate = test_status_counts[status_enum_values.index(RunStatusEnum.PASS)] / sum(test_status_counts)
    comparison_test_pass_rate = comparison_test_status_counts[status_enum_values.index(RunStatusEnum.PASS)] / sum(
        comparison_test_status_counts
    )

    # get the overview section
    overview_section = ReportOverviewSection(
        total_test_count=total_test_count,
        total_variant_count=total_variant_count,
        total_evaluation_count=total_evaluation_count,
        test_pass_rate=test_pass_rate,
        comparison_test_pass_rate=comparison_test_pass_rate,
        delta_test_pass_rate=test_pass_rate - comparison_test_pass_rate,
        evaluation_pass_rate=get_suite_run.pass_rate,
        comparison_evaluation_pass_rate=get_comparison_run.pass_rate,
        delta_evaluation_pass_rate=get_suite_run.pass_rate - get_comparison_run.pass_rate,
        run_statuses=status_enum_values,
        test_status_counts=test_status_counts,
        comparison_test_status_counts=comparison_test_status_counts,
        evaluation_status_counts=evaluation_status_counts,
        comparison_evaluation_status_counts=comparison_evaluation_status_counts,
    )

    # get the performance section
    avg_runtime = sum(evaluation_runtimes) / len(evaluation_runtimes)
    comparison_avg_runtime = sum(comparison_evaluation_runtimes) / len(comparison_evaluation_runtimes)

    performance_data = calculate_performance_buckets(evaluation_runtimes, comparison_evaluation_runtimes)

    performance_section = ReportPerformanceSection(
        average_run_time=avg_runtime,
        comparison_average_run_time=comparison_avg_runtime,
        improvement_rate=(avg_runtime - comparison_avg_runtime) / comparison_avg_runtime * -1,
        buckets=performance_data["buckets"],
        values=performance_data["values"],
        comparison_values=performance_data["comparison_values"],
        test_performances=test_worst_performance,
    )

    # return final result
    return ReportResponse(
        suite_run_id=suite_run_id,
        suite_run_timestamp=get_suite_run.created_at,
        comparison_run_id=get_comparison_run.id,
        comparison_run_timestamp=get_comparison_run.created_at,
        suite_name=get_suite.name,
        tests=tests_list,
        overview=overview_section,
        improvements=ReportImprovementSection(test_improvements=test_improvements),
        failures=ReportFailureSection(test_failures=test_failures),
        performance=performance_section,
    )
