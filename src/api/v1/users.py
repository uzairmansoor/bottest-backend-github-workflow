from fastapi import APIRouter, Depends

from src.core import bots
from src.models.api_schema import ListBotReadResponse
from src.utils import get_actor

router = APIRouter(prefix="/users")


@router.get(
    "/{user_id}/bots",
    response_model=ListBotReadResponse,
    response_model_exclude_none=True,
    tags=["Users"],
)
async def get_users_id_bots(user_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1):
    return bots.get_bots_by_user_id(user_id, actor, limit, page)
