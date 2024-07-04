from fastapi import APIRouter, Depends

from src.core import environments, suite_runs, test_runs
from src.models.api_schema import (
    EnvironmentCreateRequest,
    EnvironmentReadResponse,
    EnvironmentUpdateRequest,
    ListSuiteRunReadResponse,
    ListTestRunReadResponse,
)
from src.utils import get_actor

router = APIRouter(prefix="/environments")


@router.post("", response_model=EnvironmentReadResponse, response_model_exclude_none=True, tags=["Environments"])
async def post_environments(request: EnvironmentCreateRequest, actor: dict = Depends(get_actor)):
    return environments.create_environment(request, actor)


@router.patch(
    "/{environment_id}", response_model=EnvironmentReadResponse, response_model_exclude_none=True, tags=["Environments"]
)
async def patch_environments_id(
    request: EnvironmentUpdateRequest, environment_id: str, actor: dict = Depends(get_actor)
):
    return environments.update_environment_by_id(request, environment_id, actor)


@router.get(
    "/{environment_id}", response_model=EnvironmentReadResponse, response_model_exclude_none=True, tags=["Environments"]
)
async def get_environments_id(environment_id: str, actor: dict = Depends(get_actor)):
    return environments.get_environment_by_id(environment_id, actor)


@router.delete("/{environment_id}", tags=["Environments"])
async def delete_environments_id(environment_id: str, actor: dict = Depends(get_actor)):
    return environments.delete_environment_by_id(environment_id, actor)


@router.get(
    "/{environment_id}/suite_runs",
    response_model=ListSuiteRunReadResponse,
    response_model_exclude_none=True,
    tags=["Environments"],
)
async def get_environments_id_suite_runs(
    environment_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1
):
    return suite_runs.get_suite_runs_by_environment_id(environment_id, actor, limit, page)


@router.get(
    "/{environment_id}/test_runs",
    response_model=ListTestRunReadResponse,
    response_model_exclude_none=True,
    tags=["Environments"],
)
async def get_environments_id_test_runs(
    environment_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1
):
    return test_runs.get_test_runs_by_environment_id(environment_id, actor, limit, page)
