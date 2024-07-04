from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.orm.session import Session

from src.core.utils import has_viewer_permissions
from src.db import with_db_session
from src.models.api_schema import (
    InvalidPermissionsResponse,
    ListTestRunReadResponse,
    NotFoundResponse,
    PaginationData,
    TestRunCreateRequest,
    TestRunReadResponse,
)
from src.models.db_schema import Environment, SuiteRun, Test, TestRun
from src.models.enums import RunStatusEnum


@with_db_session
def create_test_run(request: TestRunCreateRequest, actor: dict, db_session: Session):
    get_environment = db_session.get(Environment, request.environment_id)

    if not has_viewer_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    new_test_run = TestRun.model_validate(
        request.model_dump()
        | {
            "status": RunStatusEnum.RUNNING,
            "status_info": "0",
            "created_by": actor.get("id", "unknown"),
            "last_updated_by": actor.get("id", "unknown"),
        }
    )
    db_session.add(new_test_run)
    db_session.commit()
    db_session.refresh(new_test_run)

    return TestRunReadResponse.model_validate(new_test_run)


@with_db_session
def get_test_run_by_id(test_run_id: str, actor: dict, db_session: Session):
    get_test_run = db_session.get(TestRun, test_run_id)

    if not get_test_run:
        return NotFoundResponse(TestRun)

    if not has_viewer_permissions(actor, get_test_run.environment.bot):
        return InvalidPermissionsResponse()

    return TestRunReadResponse.model_validate(get_test_run)


@with_db_session
def get_test_runs_by_test_id(
    test_id: str, actor: dict, environment_id: str | None, limit: int, page: int, db_session: Session
):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_viewer_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    db_query = select(TestRun).where(TestRun.test_id == test_id)

    if environment_id:
        db_query = db_query.where(TestRun.environment_id == environment_id)

    offset = (page - 1) * limit
    get_test_runs = db_session.exec(db_query.order_by(TestRun.created_at.desc()).limit(limit).offset(offset)).all()
    return ListTestRunReadResponse(
        data=[TestRunReadResponse.model_validate(test_run) for test_run in get_test_runs],
        pagination=PaginationData(items_len=len(get_test_runs), limit=limit, page=page),
    )


@with_db_session
def get_test_runs_by_suite_run_id(suite_run_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_suite_run = db_session.get(SuiteRun, suite_run_id)

    if not get_suite_run:
        return NotFoundResponse(SuiteRun)

    if not has_viewer_permissions(actor, get_suite_run.environment.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_test_runs = db_session.exec(
        select(TestRun)
        .where(TestRun.suite_run_id == suite_run_id)
        .order_by(TestRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return ListTestRunReadResponse(
        data=[TestRunReadResponse.model_validate(test_run) for test_run in get_test_runs],
        pagination=PaginationData(items_len=len(get_suite_run.test_runs), limit=limit, page=page),
    )


@with_db_session
def get_test_runs_by_environment_id(environment_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_environment = db_session.get(Environment, environment_id)

    if not get_environment:
        return NotFoundResponse(Environment)

    if not has_viewer_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_test_runs = db_session.exec(
        select(TestRun)
        .where(TestRun.environment_id == environment_id)
        .order_by(TestRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return ListTestRunReadResponse(
        data=[TestRunReadResponse.model_validate(test_run) for test_run in get_test_runs],
        pagination=PaginationData(items_len=len(get_environment.test_runs), limit=limit, page=page),
    )


@with_db_session
def test_run_stop_by_id(test_run_id: str, actor: dict, db_session: Session):
    get_test_run = db_session.get(TestRun, test_run_id)

    if not get_test_run:
        return NotFoundResponse(TestRun)

    if not has_viewer_permissions(actor, get_test_run.environment.bot):
        return InvalidPermissionsResponse()

    get_test_run.status = RunStatusEnum.STOPPED
    get_test_run.status_info = "Stopped by user."
    get_test_run.last_updated_at = datetime.now(timezone.utc)
    get_test_run.last_updated_by = actor.get("id", "unknown")
    db_session.commit()

    return TestRunReadResponse.model_validate(get_test_run)
