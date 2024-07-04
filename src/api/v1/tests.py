from fastapi import APIRouter, BackgroundTasks, Depends

from src.core import baselines, test_runs, tests, variants
from src.models.api_schema import (
    ListBaselineReadResponse,
    ListTestRunReadResponse,
    ListVariantReadResponse,
    TestCreateRequest,
    TestReadResponse,
    TestUpdateRequest,
)
from src.utils import get_actor

router = APIRouter(prefix="/tests")


@router.post("", response_model=TestReadResponse, response_model_exclude_none=True, tags=["Tests"])
async def post_tests(request: TestCreateRequest, actor: dict = Depends(get_actor)):
    return tests.create_test(request, actor)


@router.patch("/{test_id}", response_model=TestReadResponse, response_model_exclude_none=True, tags=["Tests"])
async def patch_tests_id(
    request: TestUpdateRequest,
    test_id: str,
    background_tasks: BackgroundTasks,
    actor: dict = Depends(get_actor),
):
    response = tests.update_test_by_id(request, test_id, actor)

    if not isinstance(response, TestReadResponse):
        return response

    # If the variant_count has changed, we may need to generate/remove additional variants
    if request.variant_count is not None:
        background_tasks.add_task(variants.manage_additional_variants, test_id)

    return response


@router.get("/{test_id}", response_model=TestReadResponse, response_model_exclude_none=True, tags=["Tests"])
async def get_tests_id(test_id: str, actor: dict = Depends(get_actor), environment_id: str | None = None):
    return tests.get_test_by_id(test_id, actor, environment_id)


@router.delete("/{test_id}", tags=["Tests"])
async def delete_tests_id(test_id: str, actor: dict = Depends(get_actor)):
    return tests.delete_test_by_id(test_id, actor)


@router.get(
    "/{test_id}/test_runs", response_model=ListTestRunReadResponse, response_model_exclude_none=True, tags=["Tests"]
)
async def get_tests_id_test_runs(
    test_id: str,
    actor: dict = Depends(get_actor),
    environment_id: str | None = None,
    limit: int = 10,
    page: int = 1,
):
    return test_runs.get_test_runs_by_test_id(test_id, actor, environment_id, limit, page)


@router.get(
    "/{test_id}/baselines", response_model=ListBaselineReadResponse, response_model_exclude_none=True, tags=["Tests"]
)
async def get_tests_id_baselines(test_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1):
    return baselines.get_baselines_by_test_id(test_id, actor, limit, page)


@router.get(
    "/{test_id}/variants", response_model=ListVariantReadResponse, response_model_exclude_none=True, tags=["Tests"]
)
async def get_tests_id_variants(test_id: str, actor: dict = Depends(get_actor), limit: int = 10, page: int = 1):
    return variants.get_variants_by_test_id(test_id, actor, limit, page)
