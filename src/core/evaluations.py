from datetime import datetime, timezone

from sqlmodel.orm.session import Session

from src.core.utils import (
    has_viewer_permissions,
    make_json_openai_request,
    parse_conversation_dict_from_html,
)
from src.db import with_db_session
from src.models.api_schema import (
    EvaluationCreateRequest,
    EvaluationReadResponse,
    InvalidPermissionsResponse,
    NotFoundResponse,
)
from src.models.db_schema import Bot, Evaluation, SuiteRun, Test, TestRun, VariantRun
from src.models.enums import RunStatusEnum
from src.settings import logger


def summarize_failure_reasons(failure_reasons: list):
    # For now stub to reduce costs
    return "stubbed_failure_reason"

    # If only one failure reason, no need to summary
    if len(failure_reasons) == 1:
        return failure_reasons[0]

    messages = [
        {
            "role": "system",
            "content": (
                "Summarize the following one sentence reasons as to why the test failed into a single sentence. Your"
                " response should be in JSON format like so: { summary: SUMMARY_HERE }"
            ),
        },
        {
            "role": "user",
            "content": "\n".join(failure_reasons),
        },
    ]
    response = make_json_openai_request(messages)
    return response.get("summary", "Could not parse failure reason from AI response.")


def evaluate_against_baseline(
    success_criteria: str, baseline_conversation_json: dict, evaluation_conversation_json: dict
):
    # For now stub to reduce costs
    from random import choice

    if success_criteria == "always pass":
        return {"pass": True}
    elif success_criteria == "always fail":
        return {"pass": False, "reason": "always failed"}

    return choice([{"pass": True}, {"pass": False, "reason": "randomly failed"}])

    system_role = (
        "You are a helpful assistant who is responsible for determining if a BASELINE matches the content of a TEST."
        " You must compare each response from the chatbot in the TEST conversation with the corresponding response in"
        " the BASELINE. If you cannot find a corresponding matching response, fail the test. Each response from the"
        " chatbot in TEST must meet the success criteria, or you will FAIL the test. Carefully reason through why the"
        " test passes or fails. Respond in JSON format, either as { pass: true } OR { pass: false, reason: REASON_HERE"
        " }, where REASON_HERE is a two sentence summary as to why the test failed.\n\nThe success criteria for the"
        " conversation is: "
        + success_criteria
    )

    messages = [
        {"role": "system", "content": system_role},
        {
            "role": "user",
            "content": f"BASELINE: {baseline_conversation_json}\n\nTEST: {evaluation_conversation_json}",
        },
    ]

    return make_json_openai_request(messages)


@with_db_session
def evaluate_conversation(evaluation_id: str, db_session: Session):
    logger.info(f"Starting evaluation for evaluation_id: {evaluation_id}")

    get_evaluation: Evaluation = db_session.get(Evaluation, evaluation_id)
    get_variant_run: VariantRun = get_evaluation.variant_run
    get_test_run: TestRun = get_variant_run.test_run
    get_test: Test = get_test_run.test

    # If test run stopped, early exit
    if get_test_run.status == RunStatusEnum.STOPPED:
        return

    # This inner function stores all logic for actual evaluation
    inner_evaluate_conversation(get_evaluation, db_session)
    db_session.commit()

    # It is structured in this way to allow for post-processing below
    # Where we can update/bubble up completed runs and check if a full test/suite run is complete
    error_flag = False

    # ----- Bubble up evaluation ----- #
    evaluation_pr_dist = []  # pr_dist = pass rate distrubution
    evaluation_res_dist = []  # res_dist = replayed elapsed seconds distribution
    evaluation_failure_reasons = []

    completed_evals = 0
    for evaluation in get_variant_run.evaluations:
        if evaluation.status == RunStatusEnum.RUNNING:
            # Return early if any evaluation is still running, can't bubble up yet
            return
        elif evaluation.status == RunStatusEnum.PASS:
            evaluation_pr_dist.append(1)
        elif evaluation.status == RunStatusEnum.FAIL:
            evaluation_pr_dist.append(0)
            evaluation_failure_reasons.append(evaluation.status_info)
        elif evaluation.status == RunStatusEnum.ERROR:
            error_flag = True
        evaluation_res_dist.append(evaluation.replayed_elapsed_seconds)
        completed_evals += 1

    # If not all evals completed, return early
    if completed_evals < get_test.iteration_count:
        return

    # If here, means all evaluations are complete
    # We can update variant_run as complete with information
    if error_flag:
        get_variant_run.status = RunStatusEnum.ERROR
        get_variant_run.status_info = "One or more evaluations contained an error."
    else:
        # Calculate pass rate and average res
        get_variant_run.pass_rate = sum(evaluation_pr_dist) / len(evaluation_pr_dist)
        get_variant_run.average_replayed_elapsed_seconds = sum(evaluation_res_dist) / len(evaluation_res_dist)

        # All evaluations passed for this variant
        if get_variant_run.pass_rate == 1:
            get_variant_run.status = RunStatusEnum.PASS
            get_variant_run.status_info = None

        else:
            # All evaluations failed for this variant
            if get_variant_run.pass_rate == 0:
                get_variant_run.status = RunStatusEnum.FAIL

            # Mixed results
            else:
                get_variant_run.status = RunStatusEnum.MIXED

            get_variant_run.status_info = summarize_failure_reasons(evaluation_failure_reasons)
    get_variant_run.completed_at = datetime.now(timezone.utc)
    db_session.commit()

    # ----- Bubble up variant run ----- #
    variant_runs_pr_dist = []  # pr_dist = pass rate distrubution
    variant_runs_res_dist = []  # res_dist = replayed elapsed seconds distribution
    variant_runs_failure_reasons = []

    completed_variants = 0
    for variant_run in get_test_run.variant_runs:
        if variant_run.status == RunStatusEnum.RUNNING:
            # Return early if any variant run is still running, can't bubble up yet
            return
        elif variant_run.status == RunStatusEnum.PASS:
            variant_runs_pr_dist.append(1)
        elif variant_run.status == RunStatusEnum.FAIL:
            variant_runs_pr_dist.append(0)
            variant_runs_failure_reasons.append(variant_run.status_info)
        elif variant_run.status == RunStatusEnum.MIXED:
            variant_runs_pr_dist.append(variant_run.pass_rate)
            variant_runs_failure_reasons.append(variant_run.status_info)
        elif variant_run.status == RunStatusEnum.ERROR:
            error_flag = True
        variant_runs_res_dist.append(variant_run.average_replayed_elapsed_seconds)
        completed_variants += 1

    # If not all variants completed, return early
    if completed_variants < get_test.variant_count:
        return

    # If here, means all variant runs are complete
    # We can update test_run as complete with information
    if error_flag:
        get_test_run.status = RunStatusEnum.ERROR
        get_test_run.status_info = "One or more variant runs contained an error."
    else:
        # Calculate pass rate and average res
        get_test_run.pass_rate = sum(variant_runs_pr_dist) / len(variant_runs_pr_dist)
        get_test_run.average_replayed_elapsed_seconds = sum(variant_runs_res_dist) / len(variant_runs_res_dist)

        # Perfect pass rate
        if get_test_run.pass_rate == 1:
            get_test_run.status = RunStatusEnum.PASS
            get_test_run.status_info = None

        else:
            # Perfect fail rate
            if get_test_run.pass_rate == 0:
                get_test_run.status = RunStatusEnum.FAIL

            # Mixed results
            else:
                get_test_run.status = RunStatusEnum.MIXED

            get_test_run.status_info = summarize_failure_reasons(variant_runs_failure_reasons)
    get_test_run.completed_at = datetime.now(timezone.utc)
    db_session.commit()

    # ----- Bubble up test run ----- #
    get_suite_run: SuiteRun = get_test_run.suite_run
    # Return if not a part of a suite run
    if not get_suite_run:
        return

    test_runs_pr_dist = []  # pr_dist = pass rate distrubution
    test_runs_res_dist = []  # res_dist = replayed elapsed seconds distribution
    test_runs_failure_reasons = []

    completed_tests = 0
    for test_run in get_suite_run.test_runs:
        if test_run.status == RunStatusEnum.RUNNING:
            # Return early if any test run is still running, can't bubble up yet
            return
        elif test_run.status == RunStatusEnum.PASS:
            test_runs_pr_dist.append(1)
        elif test_run.status == RunStatusEnum.FAIL:
            test_runs_pr_dist.append(0)
            test_runs_failure_reasons.append(test_run.status_info)
        elif test_run.status == RunStatusEnum.MIXED:
            test_runs_pr_dist.append(test_run.pass_rate)
            test_runs_failure_reasons.append(test_run.status_info)
        elif test_run.status == RunStatusEnum.ERROR:
            error_flag = True
        test_runs_res_dist.append(test_run.average_replayed_elapsed_seconds)
        completed_tests += 1

    # If not all tests completed, return early
    # FIXME: fix for when disabling tests to run
    if completed_tests < len(get_suite_run.suite.tests):
        return

    # If here, means all test runs are complete
    # We can update suite run as complete with information
    if error_flag:
        get_suite_run.status = RunStatusEnum.ERROR
        get_suite_run.status_info = "One or more test runs contained an error."
    else:
        # Calculate pass rate and average res
        get_suite_run.pass_rate = sum(test_runs_pr_dist) / len(test_runs_pr_dist)
        get_suite_run.average_replayed_elapsed_seconds = sum(test_runs_res_dist) / len(test_runs_res_dist)

        # Perfect pass rate
        if get_suite_run.pass_rate == 1:
            get_suite_run.status = RunStatusEnum.PASS
            get_suite_run.status_info = None

        else:
            # Perfect fail rate
            if get_suite_run.pass_rate == 0:
                get_suite_run.status = RunStatusEnum.FAIL

            # Mixed results
            else:
                get_suite_run.status = RunStatusEnum.MIXED

            get_suite_run.status_info = summarize_failure_reasons(test_runs_failure_reasons)
    get_suite_run.completed_at = datetime.now(timezone.utc)
    db_session.commit()


def inner_evaluate_conversation(get_evaluation: Evaluation, db_session: Session):
    get_test: Test = db_session.get(Test, get_evaluation.variant_run.test_run.test_id)
    get_bot: Bot = get_test.suite.bot

    # parse out conversation_json from html_blob
    # check if bot has selector set
    if not get_bot.query_selector:
        ai_response = parse_conversation_dict_from_html(get_evaluation.html_blob, get_selector=True)
        selector = ai_response.get("selector", None)

        # Update bot with selector query
        if selector:
            get_bot.query_selector = selector
    else:
        ai_response = parse_conversation_dict_from_html(get_evaluation.html_blob)
    conversation_dict = ai_response.get("conversation", {})

    if not conversation_dict:
        get_evaluation.status = RunStatusEnum.ERROR
        get_evaluation.status_info = "Could not parse conversation from HTML blob."
        return

    get_evaluation.conversation_json = conversation_dict

    # get required information for evaluation
    get_baselines = get_test.baselines
    if get_test.success_criteria:
        get_success_criteria = get_test.success_criteria
    else:
        get_success_criteria = get_test.suite.default_success_criteria

    # store failure reasons across multiple baselines
    baseline_failure_reasons = []

    # for each baseline in the test
    for baseline in get_baselines:
        if not baseline.conversation_json:
            get_evaluation.status = RunStatusEnum.ERROR
            get_evaluation.status_info = "Baseline does not have conversation JSON."
            return

        evaluation = evaluate_against_baseline(
            get_success_criteria, baseline.conversation_json, get_evaluation.conversation_json
        )
        did_pass = evaluation.get("pass", None)

        # Unexpected response from AI
        if did_pass is None:
            get_evaluation.status = RunStatusEnum.ERROR
            get_evaluation.status_info = "Could not parse response from AI when evaluating conversation."
            return

        # If passed, can return from function
        elif did_pass:
            get_evaluation.pass_baseline_id = baseline.id
            get_evaluation.status = RunStatusEnum.PASS
            get_evaluation.completed_at = datetime.now(timezone.utc)
            return

        # Otherwise, store failure reason
        elif evaluation.get("reason", False):
            baseline_failure_reasons.append(evaluation["reason"])

    # If here, means no baselines passed
    get_evaluation.status = RunStatusEnum.FAIL
    if len(baseline_failure_reasons) > 1:
        get_evaluation.status_info = summarize_failure_reasons(baseline_failure_reasons)
    else:
        get_evaluation.status_info = baseline_failure_reasons[0]
    get_evaluation.completed_at = datetime.now(timezone.utc)


@with_db_session
def create_evaluation(request: EvaluationCreateRequest, actor: dict, db_session: Session):
    # Check that actor has permission to read bot
    variant_run = db_session.get(VariantRun, request.variant_run_id)

    if not has_viewer_permissions(actor, variant_run.test_run.environment.bot):
        return InvalidPermissionsResponse()

    # create evaluation object
    create_dict = {
        "created_by": actor.get("id", "unknown"),
        "last_updated_by": actor.get("id", "unknown"),
        "status": RunStatusEnum.RUNNING,
    }

    new_evaluation = Evaluation.model_validate(request.model_dump() | create_dict)
    db_session.add(new_evaluation)
    db_session.commit()
    db_session.refresh(new_evaluation)

    return EvaluationReadResponse.model_validate(new_evaluation)


@with_db_session
def get_evaluation_by_id(evaluation_id: str, actor: dict, db_session: Session):
    get_evaluation = db_session.get(Evaluation, evaluation_id)

    if not get_evaluation:
        return NotFoundResponse(Evaluation)

    if not has_viewer_permissions(actor, get_evaluation.variant_run.test_run.environment.bot):
        return InvalidPermissionsResponse()

    return EvaluationReadResponse.model_validate(get_evaluation)
