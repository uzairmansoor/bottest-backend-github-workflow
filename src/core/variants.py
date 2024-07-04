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
    ListVariantReadResponse,
    NotFoundResponse,
    PaginationData,
    VariantCreateRequest,
    VariantReadResponse,
    VariantUpdateRequest,
)
from src.models.db_schema import Test, Variant


@with_db_session
def create_variant(request: VariantCreateRequest, actor: dict, db_session: Session):
    test = db_session.get(Test, request.test_id)

    if not has_editor_permissions(actor, test.suite.bot):
        return InvalidPermissionsResponse()

    new_variant = Variant.model_validate(
        request.model_dump() | {"created_by": actor.get("id", "unknown"), "last_updated_by": actor.get("id", "unknown")}
    )
    db_session.add(new_variant)
    db_session.commit()
    db_session.refresh(new_variant)

    return VariantReadResponse.model_validate(new_variant)


@with_db_session
def get_variant_by_id(variant_id: str, actor: dict, db_session: Session):
    get_variant = db_session.get(Variant, variant_id)

    if not get_variant:
        return NotFoundResponse(Variant)

    if not has_viewer_permissions(actor, get_variant.test.suite.bot):
        return InvalidPermissionsResponse()

    return VariantReadResponse.model_validate(get_variant)


@with_db_session
def update_variant_by_id(request: VariantUpdateRequest, variant_id: str, actor: dict, db_session: Session):
    get_variant = db_session.get(Variant, variant_id)

    if not get_variant:
        return NotFoundResponse(Variant)

    if not has_editor_permissions(actor, get_variant.test.suite.bot):
        return InvalidPermissionsResponse()

    get_variant = update_db_model_with_request(get_variant, request, db_session, actor)

    return VariantReadResponse.model_validate(get_variant)


@with_db_session
def delete_variant_by_id(variant_id: str, actor: dict, db_session: Session):
    get_variant = db_session.get(Variant, variant_id)

    if not get_variant:
        return NotFoundResponse(Variant)

    if not has_editor_permissions(actor, get_variant.test.suite.bot):
        return InvalidPermissionsResponse()

    db_session.delete(get_variant)
    db_session.commit()

    return {"status": "OK"}


@with_db_session
def get_variants_by_test_id(test_id: str, actor: dict, limit: int, page: int, db_session: Session):
    get_test = db_session.get(Test, test_id)

    if not get_test:
        return NotFoundResponse(Test)

    if not has_viewer_permissions(actor, get_test.suite.bot):
        return InvalidPermissionsResponse()

    offset = (page - 1) * limit
    get_variants = db_session.exec(
        select(Variant)
        .where(Variant.test_id == test_id)
        .order_by(Variant.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return ListVariantReadResponse(
        data=[VariantReadResponse.model_validate(variant) for variant in get_variants],
        pagination=PaginationData(items_len=len(get_test.variants), limit=limit, page=page),
    )


@with_db_session
def manage_additional_variants(test_id: str, db_session: Session):
    get_test = db_session.get(Test, test_id)
    get_variant = get_test.variants[0]

    # Check if number of variants is less than the desired count
    set_variant_count = get_variant.test.variant_count
    existing_variant_count = len(get_variant.test.variants)
    need_to_generate = set_variant_count - existing_variant_count

    # generate new variants
    if need_to_generate > 0:
        for _ in range(need_to_generate):
            new_variant = Variant.model_validate(
                {
                    "test_id": get_variant.test_id,
                    # FIXME: Generate replay_json dont just copy for future
                    "replay_json": get_variant.replay_json,
                    "created_by": get_variant.created_by,
                    "last_updated_by": get_variant.last_updated_by,
                }
            )
            db_session.add(new_variant)
        db_session.commit()

    # delete extra variants
    elif need_to_generate < 0:
        extra_variants = db_session.exec(
            select(Variant)
            .where(Variant.test_id == get_variant.test_id)
            .order_by(Variant.created_at.desc())
            .limit(abs(need_to_generate))
        )
        for variant in extra_variants:
            db_session.delete(variant)
        db_session.commit()
