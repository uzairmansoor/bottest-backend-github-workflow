from sqlmodel import select
from sqlmodel.orm.session import Session

from src.core.utils import (
    has_editor_permissions,
    has_viewer_permissions,
    update_db_model_with_request,
)
from src.db import with_db_session
from src.models.api_schema import (
    EnvironmentCreateRequest,
    EnvironmentReadResponse,
    EnvironmentUpdateRequest,
    InvalidPermissionsResponse,
    ListEnvironmentReadResponse,
    NotFoundResponse,
    PaginationData,
)
from src.models.db_schema import Bot, Environment


@with_db_session
def create_environment(request: EnvironmentCreateRequest, actor: dict, db_session: Session):
    get_bot = db_session.get(Bot, request.bot_id)

    if not has_editor_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    new_environment = Environment.model_validate(
        request.model_dump() | {"created_by": actor.get("id", "unknown"), "last_updated_by": actor.get("id", "unknown")}
    )
    db_session.add(new_environment)
    db_session.commit()
    db_session.refresh(new_environment)

    return EnvironmentReadResponse.model_validate(new_environment)


@with_db_session
def update_environment_by_id(request: EnvironmentUpdateRequest, environment_id: str, actor: dict, db_session: Session):
    get_environment = db_session.get(Environment, environment_id)

    if not get_environment:
        return NotFoundResponse(Environment)

    if not has_editor_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    get_environment = update_db_model_with_request(get_environment, request, db_session, actor)
    return EnvironmentReadResponse.model_validate(get_environment)


@with_db_session
def get_environment_by_id(environment_id: str, actor: dict, db_session: Session):
    get_environment = db_session.get(Environment, environment_id)

    if not get_environment:
        return NotFoundResponse(Environment)

    if not has_viewer_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    return EnvironmentReadResponse.model_validate(get_environment)


@with_db_session
def delete_environment_by_id(environment_id: str, actor: dict, db_session: Session):
    get_environment = db_session.get(Environment, environment_id)

    if not get_environment:
        return NotFoundResponse(Environment)

    if not has_editor_permissions(actor, get_environment.bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_environment)
    db_session.commit()
    return {"status": "OK"}


@with_db_session
def get_environments_by_bot_id(bot_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_viewer_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_environments = db_session.exec(
        select(Environment)
        .where(Environment.bot_id == bot_id)
        .order_by(Environment.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return ListEnvironmentReadResponse(
        data=[EnvironmentReadResponse.model_validate(environment) for environment in get_environments],
        pagination=PaginationData(items_len=len(get_bot.environments), limit=limit, page=page),
    )
