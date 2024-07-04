from sqlmodel import select
from sqlmodel.orm.session import Session

from src.core.utils import (
    has_editor_permissions,
    has_viewer_permissions,
    parse_conversation_dict_from_html,
)
from src.db import with_db_session
from src.models.api_schema import (
    BaselineCreateRequest,
    BaselineReadResponse,
    InvalidPermissionsResponse,
    ListBaselineReadResponse,
    NotFoundResponse,
    PaginationData,
)
from src.models.db_schema import Baseline, Bot, Test


@with_db_session
def create_baseline(request: BaselineCreateRequest, actor: dict, db_session: Session):
    test = db_session.get(Test, request.test_id)
    if not has_editor_permissions(actor, test.suite.bot):
        return InvalidPermissionsResponse()

    new_baseline = Baseline.model_validate(
        request.model_dump() | {"created_by": actor.get("id", "unknown"), "last_updated_by": actor.get("id", "unknown")}
    )
    db_session.add(new_baseline)
    db_session.commit()
    db_session.refresh(new_baseline)

    return BaselineReadResponse.model_validate(new_baseline)


@with_db_session
def get_baseline_by_id(baseline_id: str, actor: dict, db_session: Session):
    get_baseline = db_session.get(Baseline, baseline_id)

    if not get_baseline:
        return NotFoundResponse(Baseline)

    if not has_viewer_permissions(actor, get_baseline.test.suite.bot):
        return InvalidPermissionsResponse()

    return BaselineReadResponse.model_validate(get_baseline)


@with_db_session
def delete_baseline_by_id(baseline_id: str, actor: dict, db_session: Session):
    get_baseline = db_session.get(Baseline, baseline_id)

    if not get_baseline:
        return NotFoundResponse(Baseline)

    if not has_editor_permissions(actor, get_baseline.test.suite.bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_baseline)
    db_session.commit()

    return {"status": "OK"}


@with_db_session
def get_baselines_by_test_id(test_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_viewer_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_baselines = db_session.exec(
        select(Baseline)
        .where(Baseline.test_id == test_id)
        .order_by(Baseline.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return ListBaselineReadResponse(
        data=[BaselineReadResponse.model_validate(baseline) for baseline in get_baselines],
        pagination=PaginationData(items_len=len(get_test.baselines), limit=limit, page=page),
    )


@with_db_session
def populate_conversation_json(baseline_id: str, db_session: Session):
    get_baseline: Baseline = db_session.get(Baseline, baseline_id)
    get_bot: Bot = get_baseline.test.suite.bot

    if not get_bot.query_selector:
        ai_response = parse_conversation_dict_from_html(get_baseline.html_blob, get_selector=True, baseline=True)
        selector = ai_response.get("selector", None)

        # Update bot with selector query
        if selector:
            get_bot.query_selector = selector
    else:
        ai_response = parse_conversation_dict_from_html(get_baseline.html_blob, baseline=True)
    conversation_dict = ai_response.get("conversation", {})

    get_baseline.conversation_json = conversation_dict
    db_session.commit()
