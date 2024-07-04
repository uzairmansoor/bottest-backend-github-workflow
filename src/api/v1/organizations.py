from fastapi import APIRouter, Depends

from src.core import bots
from src.models.api_schema import ListBotReadResponse
from src.utils import get_actor

router = APIRouter(prefix="/organizations")


@router.get(
    "/{organization_id}/bots",
    response_model=ListBotReadResponse,
    response_model_exclude_none=True,
    tags=["Organizations"],
)
async def get_organizations_id_bots(
    organization_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1
):
    return bots.get_bots_by_organization_id(organization_id, actor, limit, page)
