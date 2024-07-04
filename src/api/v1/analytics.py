from fastapi import APIRouter, Depends

from src.core import analytics
from src.models.api_schema import (
    ReportResponse,
    TrendingPerformance,
    TrendingSuccess,
    TrendingUsage,
)
from src.utils import get_actor

router = APIRouter(prefix="/analytics")


@router.get(
    "/trending/success",
    response_model=TrendingSuccess,
    response_model_exclude_none=True,
    tags=["Analytics"],
)
async def get_trending_success(suite_id: str, environment_id: str, actor: dict = Depends(get_actor)):
    return analytics.get_success_data(suite_id, environment_id, actor)


@router.get(
    "/trending/performance",
    response_model=TrendingPerformance,
    response_model_exclude_none=True,
    tags=["Analytics"],
)
async def get_trending_performance(suite_id: str, environment_id: str, actor: dict = Depends(get_actor)):
    return analytics.get_performance_data(suite_id, environment_id, actor)


@router.get(
    "/trending/usage",
    response_model=TrendingUsage,
    response_model_exclude_none=True,
    tags=["Analytics"],
)
async def get_trending_usage(suite_id: str, environment_id: str, actor: dict = Depends(get_actor)):
    return analytics.get_usage_data(suite_id, environment_id, actor)


@router.get(
    "/report",
    response_model=ReportResponse,
    response_model_exclude_none=True,
    tags=["Analytics"],
)
async def get_report(suite_run_id: str, actor: dict = Depends(get_actor)):
    return analytics.get_report_data(suite_run_id, actor)
