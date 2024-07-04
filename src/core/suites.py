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
    ListSuiteReadResponse,
    NotFoundResponse,
    PaginationData,
    SuiteCreateRequest,
    SuiteReadResponse,
    SuiteUpdateRequest,
)
from src.models.db_schema import Bot, Suite


@with_db_session
def create_suite(request: SuiteCreateRequest, actor: dict, db_session: Session):
    get_bot = db_session.get(Bot, request.bot_id)

    if not has_editor_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    new_suite = Suite.model_validate(
        request.model_dump() | {"created_by": actor.get("id", "unknown"), "last_updated_by": actor.get("id", "unknown")}
    )

    db_session.add(new_suite)
    db_session.commit()
    db_session.refresh(new_suite)

    return SuiteReadResponse.model_validate(new_suite)


@with_db_session
def update_suite_by_id(request: SuiteUpdateRequest, suite_id: str, actor: dict, db_session: Session):
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    # Check that actor has permission to edit bot
    if not has_editor_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    get_suite = update_db_model_with_request(get_suite, request, db_session, actor)

    return SuiteReadResponse.model_validate(get_suite)


@with_db_session
def get_suite_by_id(suite_id: str, actor: dict, db_session: Session):
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_viewer_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    return SuiteReadResponse.model_validate(get_suite)


@with_db_session
def delete_suite_by_id(suite_id: str, actor: dict, db_session: Session):
    get_suite = db_session.get(Suite, suite_id)

    if not get_suite:
        return NotFoundResponse(Suite)

    if not has_editor_permissions(actor, get_suite.bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_suite)
    db_session.commit()

    return {"status": "OK"}


@with_db_session
def get_suites_by_bot_id(bot_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_editor_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_suites = db_session.exec(
        select(Suite).where(Suite.bot_id == bot_id).order_by(Suite.created_at.desc()).limit(limit).offset(offset)
    ).all()

    return ListSuiteReadResponse(
        data=[SuiteReadResponse.model_validate(suite) for suite in get_suites],
        pagination=PaginationData(items_len=len(get_bot.suites), limit=limit, page=page),
    )
