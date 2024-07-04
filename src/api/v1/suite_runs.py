from fastapi import APIRouter, Depends

from src.core import suite_runs, test_runs
from src.models.api_schema import (
    ListTestRunReadResponse,
    SuiteRunCreateRequest,
    SuiteRunReadResponse,
)
from src.utils import get_actor

router = APIRouter(prefix="/suite_runs")


@router.post("", response_model=SuiteRunReadResponse, response_model_exclude_none=True, tags=["Suite Runs"])
async def post_suite_runs(request: SuiteRunCreateRequest, actor: dict = Depends(get_actor)):
    return suite_runs.create_suite_run(request, actor)


@router.post(
    "/{suite_run_id}/stop",
    response_model=SuiteRunReadResponse,
    response_model_exclude_none=True,
    tags=["Suite Runs"],
)
async def post_suite_runs_id_stop(suite_run_id: str, actor: dict = Depends(get_actor)):
    return suite_runs.suite_run_stop_by_id(suite_run_id, actor)


@router.get(
    "/{suite_run_id}",
    response_model=SuiteRunReadResponse,
    response_model_exclude_none=True,
    tags=["Suite Runs"],
)
async def get_suite_runs_id(suite_run_id: str, actor: dict = Depends(get_actor)):
    return suite_runs.get_suite_run_by_id(suite_run_id, actor)


@router.get(
    "/{suite_run_id}/test_runs",
    response_model=ListTestRunReadResponse,
    response_model_exclude_none=True,
    tags=["Suite Runs"],
)
async def get_suite_runs_id_test_runs(
    suite_run_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1
):
    return test_runs.get_test_runs_by_suite_run_id(suite_run_id, actor, limit, page)
