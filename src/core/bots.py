from sqlmodel import func, select
from sqlmodel.orm.session import Session

from src.core.utils import (
    has_admin_permissions,
    has_viewer_permissions,
    update_db_model_with_request,
)
from src.db import with_db_session
from src.models.api_schema import (
    BotCreateRequest,
    BotReadResponse,
    BotUpdateRequest,
    InvalidPermissionsResponse,
    ListBotReadResponse,
    NotFoundResponse,
    PaginationData,
)
from src.models.db_schema import Bot


@with_db_session
def create_bot(request: BotCreateRequest, actor: dict, db_session: Session):
    if (request.organization_id and request.user_id) or (not request.organization_id and not request.user_id):
        return {"message": "Either organization_id or user_id must be specified but not both."}

    if not has_admin_permissions(actor, request):
        return InvalidPermissionsResponse()

    new_bot = Bot.model_validate(
        request.model_dump() | {"created_by": actor.get("id", "unknown"), "last_updated_by": actor.get("id", "unknown")}
    )
    db_session.add(new_bot)
    db_session.commit()
    db_session.refresh(new_bot)

    return BotReadResponse.model_validate(new_bot)


@with_db_session
def update_bot_by_id(request: BotUpdateRequest, bot_id: str, actor: dict, db_session: Session):
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_admin_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    get_bot = update_db_model_with_request(get_bot, request, db_session, actor)

    return BotReadResponse.model_validate(get_bot)


@with_db_session
def get_bot_by_id(bot_id: str, actor: dict, db_session: Session):
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_viewer_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    return BotReadResponse.model_validate(get_bot)


@with_db_session
def delete_bot_by_id(bot_id: str, actor: dict, db_session: Session):
    get_bot = db_session.get(Bot, bot_id)

    if not get_bot:
        return NotFoundResponse(Bot)

    if not has_admin_permissions(actor, get_bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_bot)
    db_session.commit()

    return {"status": "OK"}


@with_db_session
def get_bots_by_user_id(user_id: str, actor: dict, limit: int, page: int, db_session: Session):
    # Check that actor is same as user
    if user_id != actor.get("id", "unknown"):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_bots = db_session.exec(
        select(Bot).where(Bot.user_id == user_id).order_by(Bot.created_at.desc()).limit(limit).offset(offset)
    ).all()
    count = db_session.exec(select(func.count()).where(Bot.user_id == user_id)).one()
    return ListBotReadResponse(
        data=[BotReadResponse.model_validate(bot) for bot in get_bots],
        pagination=PaginationData(items_len=count, limit=limit, page=page),
    )


@with_db_session
def get_bots_by_organization_id(organization_id: str, actor: dict, limit: int, page: int, db_session: Session):
    # Check that actor is org member
    if organization_id != actor.get("org_id", "unknown"):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_bots = db_session.exec(
        select(Bot)
        .where(Bot.organization_id == organization_id)
        .order_by(Bot.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    count = db_session.exec(select(func.count()).where(Bot.organization_id == organization_id)).one()
    return ListBotReadResponse(
        data=[BotReadResponse.model_validate(bot) for bot in get_bots],
        pagination=PaginationData(items_len=count, limit=limit, page=page),
    )
