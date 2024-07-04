from fastapi import APIRouter, Depends

from src.core import copy, suite_runs, suites, tests
from src.models.api_schema import (
    ListSuiteRunReadResponse,
    ListTestReadResponse,
    SuiteCreateRequest,
    SuiteReadResponse,
    SuiteUpdateRequest,
)
from src.utils import get_actor

router = APIRouter(prefix="/suites")


@router.post("", response_model=SuiteReadResponse, response_model_exclude_none=True, tags=["Suites"])
async def post_suites(request: SuiteCreateRequest, actor: dict = Depends(get_actor)):
    return suites.create_suite(request, actor)


@router.patch("/{suite_id}", response_model=SuiteReadResponse, response_model_exclude_none=True, tags=["Suites"])
async def patch_suites_id(request: SuiteUpdateRequest, suite_id: str, actor: dict = Depends(get_actor)):
    return suites.update_suite_by_id(request, suite_id, actor)


@router.get("/{suite_id}", response_model=SuiteReadResponse, response_model_exclude_none=True, tags=["Suites"])
async def get_suites_id(suite_id: str, actor: dict = Depends(get_actor)):
    return suites.get_suite_by_id(suite_id, actor)


@router.delete("/{suite_id}", tags=["Suites"])
async def delete_suites_id(suite_id: str, actor: dict = Depends(get_actor)):
    return suites.delete_suite_by_id(suite_id, actor)


@router.get(
    "/{suite_id}/suite_runs",
    response_model=ListSuiteRunReadResponse,
    response_model_exclude_none=True,
    tags=["Suites"],
)
async def get_suites_id_suite_runs(
    suite_id: str, actor: dict = Depends(get_actor), environment_id: str | None = None, limit: int = 10, page: int = 1
):
    return suite_runs.get_suite_runs_by_suite_id(suite_id, actor, environment_id, limit, page)


@router.get("/{suite_id}/tests", response_model=ListTestReadResponse, response_model_exclude_none=True, tags=["Suites"])
async def get_suites_id_tests(
    suite_id: str,
    actor: dict = Depends(get_actor),
    environment_id: str | None = None,
    limit: int = 10,
    page: int = 1,
):
    return tests.get_tests_by_suite_id(suite_id, actor, environment_id, limit, page)


@router.post("/{suite_id}/copy", response_model=SuiteReadResponse, response_model_exclude_none=True, tags=["Suites"])
async def post_suites_id_copy(suite_id: str, actor: dict = Depends(get_actor)):
    return copy.copy_suite_by_id(suite_id, actor)
