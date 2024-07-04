from fastapi import APIRouter, BackgroundTasks, Depends

from src.core import baselines
from src.models.api_schema import (
    BaselineCreateRequest,
    BaselineReadResponse,
    InvalidPermissionsResponse,
)
from src.utils import get_actor

router = APIRouter(prefix="/baselines")


@router.post("", response_model=BaselineReadResponse, response_model_exclude_none=True, tags=["Baselines"])
async def post_baselines(
    request: BaselineCreateRequest, background_tasks: BackgroundTasks, actor: dict = Depends(get_actor)
):
    response: BaselineReadResponse | InvalidPermissionsResponse = baselines.create_baseline(request, actor)
    if isinstance(response, InvalidPermissionsResponse):
        return response

    # parse out the convesation json from the html blob
    if not response.conversation_json:
        background_tasks.add_task(baselines.populate_conversation_json, response.id)

    return response


@router.get("/{baseline_id}", response_model=BaselineReadResponse, response_model_exclude_none=True, tags=["Baselines"])
async def get_baselines_id(baseline_id: str, actor: dict = Depends(get_actor)):
    return baselines.get_baseline_by_id(baseline_id, actor)


@router.delete("/{baseline_id}", tags=["Baselines"])
async def delete_baselines_id(baseline_id: str, actor: dict = Depends(get_actor)):
    return baselines.delete_baseline_by_id(baseline_id, actor)
