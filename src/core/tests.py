from sqlmodel import select
from sqlmodel.orm.session import Session

from src.core.utils import (
    has_editor_permissions,
    has_viewer_permissions,
    update_db_model_with_request,
)
from src.db import with_db_session
from src.models.api_schema import (
    InvalidPermissionsResponse,
    ListTestReadResponse,
    NotFoundResponse,
    PaginationData,
    RecentTestRuns,
    TestCreateRequest,
    TestReadResponse,
    TestUpdateRequest,
)
from src.models.db_schema import Suite, Test, TestRun


@with_db_session
def create_test(request: TestCreateRequest, actor: dict, db_session: Session):
    get_suite = db_session.get(Suite, request.suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_editor_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    new_test = Test.model_validate(
        (
            request.model_dump()
            | {
                "created_by": actor.get("id", "unknown"),
                "last_updated_by": actor.get("id", "unknown"),
                "success_criteria": get_suite.default_success_criteria,
                "use_default_success_criteria": True,
                "iteration_count": get_suite.default_iteration_count,
                "use_default_iteration_count": True,
                "variant_count": get_suite.default_variant_count,
                "use_default_variant_count": True,
            }
        )
    )
    db_session.add(new_test)
    db_session.commit()
    db_session.refresh(new_test)

    return TestReadResponse.model_validate(new_test)


@with_db_session
def update_test_by_id(request: TestUpdateRequest, test_id: str, actor: dict, db_session: Session):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_editor_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    get_test = update_db_model_with_request(get_test, request, db_session, actor)
    # Check for updates to the defaults
    if request.use_default_success_criteria:
        get_test.success_criteria = get_test.suite.default_success_criteria
    if request.use_default_iteration_count:
        get_test.iteration_count = get_test.suite.default_iteration_count
    if request.use_default_variant_count:
        get_test.variant_count = get_test.suite.default_variant_count

    return TestReadResponse.model_validate(get_test)


@with_db_session
def get_test_by_id(test_id: str, actor: dict, environment_id: str | None, db_session: Session):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_viewer_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    response = TestReadResponse.model_validate(get_test)

    if environment_id:
        # Get the test runs for the test in the environment
        get_test_runs = db_session.exec(
            select(TestRun)
            .where(TestRun.test_id == test_id)
            .where(TestRun.environment_id == environment_id)
            .order_by(TestRun.created_at.desc())
            .limit(11)
        ).all()
        response.recent_test_runs = [RecentTestRuns.model_validate(test_run) for test_run in get_test_runs]

    return response


@with_db_session
def delete_test_by_id(test_id: str, actor: dict, db_session: Session):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_editor_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_test)
    db_session.commit()

    return {"status": "OK"}


@with_db_session
def get_tests_by_suite_id(
    suite_id: str,
    actor: dict,
    environment_id: str | None,
    limit: int,
    page: int,
    db_session: Session,
):
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_tests = db_session.exec(
        select(Test).where(Test.suite_id == suite_id).order_by(Test.created_at.desc()).limit(limit).offset(offset)
    ).all()
    get_tests = [TestReadResponse.model_validate(test) for test in get_tests]

    # if environment passed, populate the recent test runs
    if environment_id:
        for test in get_tests:
            get_test_runs = db_session.exec(
                select(TestRun)
                .where(TestRun.test_id == test.id)
                .where(TestRun.environment_id == environment_id)
                .order_by(TestRun.created_at.desc())
                .limit(11)
            ).all()
            test.recent_test_runs = [RecentTestRuns.model_validate(test_run) for test_run in get_test_runs]

    return ListTestReadResponse(
        data=get_tests,
        pagination=PaginationData(items_len=len(get_suite.tests), limit=limit, page=page),
    )
