from fastapi import APIRouter, Depends

from src.core import bots, copy, environments, suites
from src.models.api_schema import (
    BotCreateRequest,
    BotReadResponse,
    BotUpdateRequest,
    ListEnvironmentReadResponse,
    ListSuiteReadResponse,
)
from src.utils import get_actor

router = APIRouter(prefix="/bots")


@router.post("", response_model=BotReadResponse, response_model_exclude_none=True, tags=["Bots"])
async def post_bots(request: BotCreateRequest, actor: dict = Depends(get_actor)):
    return bots.create_bot(request, actor)


@router.patch("/{bot_id}", response_model=BotReadResponse, response_model_exclude_none=True, tags=["Bots"])
async def patch_bots_id(request: BotUpdateRequest, bot_id: str, actor: dict = Depends(get_actor)):
    return bots.update_bot_by_id(request, bot_id, actor)


@router.get("/{bot_id}", response_model=BotReadResponse, response_model_exclude_none=True, tags=["Bots"])
async def get_bots_id(bot_id: str, actor: dict = Depends(get_actor)):
    return bots.get_bot_by_id(bot_id, actor)


@router.delete("/{bot_id}", tags=["Bots"])
async def delete_bots_id(bot_id: str, actor: dict = Depends(get_actor)):
    return bots.delete_bot_by_id(bot_id, actor)


@router.get(
    "/{bot_id}/environments",
    response_model=ListEnvironmentReadResponse,
    response_model_exclude_none=True,
    tags=["Bots"],
)
async def get_bots_id_environments(bot_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1):
    return environments.get_environments_by_bot_id(bot_id, actor, limit, page)


@router.get("/{bot_id}/suites", response_model=ListSuiteReadResponse, response_model_exclude_none=True, tags=["Bots"])
async def get_bots_id_suites(bot_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1):
    return suites.get_suites_by_bot_id(bot_id, actor, limit, page)


@router.post("/{bot_id}/copy", response_model=BotReadResponse, response_model_exclude_none=True, tags=["Bots"])
async def post_bots_id_copy(bot_id: str, actor: dict = Depends(get_actor)):
    return copy.copy_bot_by_id(bot_id, actor)
