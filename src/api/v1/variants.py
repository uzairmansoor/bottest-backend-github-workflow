from fastapi import APIRouter, BackgroundTasks, Depends

from src.core import variants
from src.models.api_schema import (
    InvalidPermissionsResponse,
    VariantCreateRequest,
    VariantReadResponse,
    VariantUpdateRequest,
)
from src.utils import get_actor

router = APIRouter(prefix="/variants")


@router.post("", response_model=VariantReadResponse, response_model_exclude_none=True, tags=["Variants"])
async def post_variants(
    request: VariantCreateRequest, background_tasks: BackgroundTasks, actor: dict = Depends(get_actor)
):
    response: VariantReadResponse | InvalidPermissionsResponse = variants.create_variant(request, actor)

    if isinstance(response, InvalidPermissionsResponse):
        return response

    # We may need to generate additional variants in the background using the original
    background_tasks.add_task(variants.manage_additional_variants, response.test_id)

    return response


@router.get("/{variant_id}", response_model=VariantReadResponse, response_model_exclude_none=True, tags=["Variants"])
async def get_variants_id(variant_id: str, actor: dict = Depends(get_actor)):
    return variants.get_variant_by_id(variant_id, actor)


@router.patch("/{variant_id}", response_model=VariantReadResponse, response_model_exclude_none=True, tags=["Variants"])
async def patch_variants_id(request: VariantUpdateRequest, variant_id: str, actor: dict = Depends(get_actor)):
    return variants.update_variant_by_id(request, variant_id, actor)


@router.delete("/{variant_id}", tags=["Variants"])
async def delete_variant_id(variant_id: str, actor: dict = Depends(get_actor)):
    return variants.delete_variant_by_id(variant_id, actor)
