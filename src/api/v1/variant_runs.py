from fastapi import APIRouter, Depends

from src.core import variant_runs
from src.models.api_schema import VariantRunCreateRequest, VariantRunReadResponse
from src.utils import get_actor

router = APIRouter(prefix="/variant_runs")


@router.post("", response_model=VariantRunReadResponse, response_model_exclude_none=True, tags=["Variant Runs"])
async def post_variant_runs(request: VariantRunCreateRequest, actor: dict = Depends(get_actor)):
    return variant_runs.create_variant_run(request, actor)


@router.get(
    "/{variant_run_id}", response_model=VariantRunReadResponse, response_model_exclude_none=True, tags=["Variant Runs"]
)
async def get_variant_runs_id(variant_run_id: str, actor: dict = Depends(get_actor)):
    return variant_runs.get_variant_run_by_id(variant_run_id, actor)
