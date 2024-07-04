from sqlmodel.orm.session import Session

from src.core.utils import has_viewer_permissions
from src.db import with_db_session
from src.models.api_schema import (
    InvalidPermissionsResponse,
    NotFoundResponse,
    VariantRunCreateRequest,
    VariantRunReadResponse,
)
from src.models.db_schema import TestRun, VariantRun
from src.models.enums import RunStatusEnum


@with_db_session
def create_variant_run(request: VariantRunCreateRequest, actor: dict, db_session: Session):
    get_test_run = db_session.get(TestRun, request.test_run_id)

    if not has_viewer_permissions(actor, get_test_run.environment.bot):
        return InvalidPermissionsResponse()

    new_variant_run = VariantRun.model_validate(
        request.model_dump()
        | {
            "status": RunStatusEnum.RUNNING,
            "created_by": actor.get("id", "unknown"),
            "last_updated_by": actor.get("id", "unknown"),
        }
    )
    db_session.add(new_variant_run)
    db_session.commit()
    db_session.refresh(new_variant_run)

    return VariantRunReadResponse.model_validate(new_variant_run)


@with_db_session
def get_variant_run_by_id(variant_run_id: str, actor: dict, db_session: Session):
    get_variant_run = db_session.get(VariantRun, variant_run_id)

    if not get_variant_run:
        return NotFoundResponse(VariantRun)

    if not has_viewer_permissions(actor, get_variant_run.test_run.environment.bot):
        return InvalidPermissionsResponse()

    return VariantRunReadResponse.model_validate(get_variant_run)
