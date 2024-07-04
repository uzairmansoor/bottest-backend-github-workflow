from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.orm.session import Session

from src.core.utils import has_editor_permissions, has_viewer_permissions
from src.db import with_db_session
from src.models.api_schema import (
    InvalidPermissionsResponse,
    ListSuiteRunReadResponse,
    NotFoundResponse,
    PaginationData,
    SuiteRunCreateRequest,
    SuiteRunReadResponse,
)
from src.models.db_schema import Environment, Suite, SuiteRun
from src.models.enums import RunStatusEnum


@with_db_session
def create_suite_run(request: SuiteRunCreateRequest, actor: dict, db_session: Session):
    environment = db_session.get(Environment, request.environment_id)

    if not has_editor_permissions(actor, environment.bot):
        return InvalidPermissionsResponse()

    new_suite_run = SuiteRun.model_validate(
        request.model_dump()
        | {
            "status": RunStatusEnum.RUNNING,
            "created_by": actor.get("id", "unknown"),
            "last_updated_by": actor.get("id", "unknown"),
        }
    )
    db_session.add(new_suite_run)
    db_session.commit()
    db_session.refresh(new_suite_run)

    return SuiteRunReadResponse.model_validate(new_suite_run)


@with_db_session
def get_suite_run_by_id(suite_run_id: str, actor: dict, db_session: Session):
    get_suite_run = db_session.get(SuiteRun, suite_run_id)

    if not get_suite_run:
        return NotFoundResponse(SuiteRun)

    if not has_viewer_permissions(actor, get_suite_run.environment.bot):
        return InvalidPermissionsResponse()

    return SuiteRunReadResponse.model_validate(get_suite_run)


@with_db_session
def get_suite_runs_by_suite_id(
    suite_id: str, actor: dict, environment_id: str | None, limit: int, page: int, db_session: Session
):
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    db_query = select(SuiteRun).where(SuiteRun.suite_id == suite_id)

    if environment_id:
        db_query = db_query.where(SuiteRun.environment_id == environment_id)

    offset = (page - 1) * limit
    get_suite_runs = db_session.exec(db_query.order_by(SuiteRun.created_at.desc()).limit(limit).offset(offset)).all()
    return ListSuiteRunReadResponse(
        data=[SuiteRunReadResponse.model_validate(suite_run) for suite_run in get_suite_runs],
        pagination=PaginationData(items_len=len(get_suite_runs), page=page, limit=limit),
    )


@with_db_session
def get_suite_runs_by_environment_id(environment_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_environment = db_session.get(Environment, environment_id)

    if not get_environment:
        return NotFoundResponse(Environment)

    if not has_viewer_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_suite_runs = db_session.exec(
        select(SuiteRun)
        .where(SuiteRun.environment_id == environment_id)
        .order_by(SuiteRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return ListSuiteRunReadResponse(
        data=[SuiteRunReadResponse.model_validate(suite_run) for suite_run in get_suite_runs],
        pagination=PaginationData(items_len=len(get_environment.suite_runs), page=page, limit=limit),
    )


@with_db_session
def suite_run_stop_by_id(suite_run_id: str, actor: dict, db_session: Session):
    get_suite_run = db_session.get(SuiteRun, suite_run_id)

    if not get_suite_run:
        return NotFoundResponse(SuiteRun)

    if not has_viewer_permissions(actor, get_suite_run.environment.bot):
        return InvalidPermissionsResponse()

    get_suite_run.status = RunStatusEnum.STOPPED
    get_suite_run.status_info = "Stopped by user."
    get_suite_run.last_updated_at = datetime.now(timezone.utc)
    get_suite_run.last_updated_by = actor.get("id", "unknown")

    # update all test runs
    for test_run in get_suite_run.test_runs:
        test_run.status = RunStatusEnum.STOPPED
        test_run.status_info = "Stopped by user."
        test_run.last_updated_at = datetime.now(timezone.utc)
        test_run.last_updated_by = actor.get("id", "unknown")

    db_session.commit()
    return SuiteRunReadResponse.model_validate(get_suite_run)
