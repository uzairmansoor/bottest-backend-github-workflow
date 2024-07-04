from fastapi import APIRouter, Depends

from src.core import test_runs
from src.models.api_schema import TestRunCreateRequest, TestRunReadResponse
from src.utils import get_actor

router = APIRouter(prefix="/test_runs")


@router.post("", response_model=TestRunReadResponse, response_model_exclude_none=True, tags=["Test Runs"])
async def post_test_runs(request: TestRunCreateRequest, actor: dict = Depends(get_actor)):
    return test_runs.create_test_run(request, actor)


@router.post(
    "/{test_run_id}/stop",
    response_model=TestRunReadResponse,
    response_model_exclude_none=True,
    tags=["Test Runs"],
)
async def post_test_runs_id_stop(test_run_id: str, actor: dict = Depends(get_actor)):
    return test_runs.test_run_stop_by_id(test_run_id, actor)


@router.get("/{test_run_id}", response_model=TestRunReadResponse, response_model_exclude_none=True, tags=["Test Runs"])
async def get_test_runs_id(test_run_id: str, actor: dict = Depends(get_actor)):
    return test_runs.get_test_run_by_id(test_run_id, actor)
