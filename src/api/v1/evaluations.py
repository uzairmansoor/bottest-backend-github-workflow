from fastapi import APIRouter, BackgroundTasks, Depends

from src.core import evaluations
from src.models.api_schema import (
    EvaluationCreateRequest,
    EvaluationReadResponse,
    InvalidPermissionsResponse,
)
from src.utils import get_actor

router = APIRouter(prefix="/evaluations")


@router.post("", response_model=EvaluationReadResponse, response_model_exclude_none=True, tags=["Evaluations"])
async def post_evaluations(
    request: EvaluationCreateRequest,
    background_tasks: BackgroundTasks,
    actor: dict = Depends(get_actor),
):
    response: EvaluationReadResponse | InvalidPermissionsResponse = evaluations.create_evaluation(request, actor)

    if isinstance(response, InvalidPermissionsResponse):
        return response

    # Evaluate the actual conversation in the background so we can send back a response sooner
    # Note that there still might be a delay to the reseponse as we have to process the HTML blob -> JSON using AI
    background_tasks.add_task(evaluations.evaluate_conversation, response.id)

    return response


@router.get(
    "/{evaluation_id}", response_model=EvaluationReadResponse, response_model_exclude_none=True, tags=["Evaluations"]
)
async def get_evaluations_id(evaluation_id: str, actor: dict = Depends(get_actor)):
    return evaluations.get_evaluation_by_id(evaluation_id, actor)
