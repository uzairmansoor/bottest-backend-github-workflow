from fastapi import APIRouter

from src.api.v1 import router as v1_router
from src.core.contact import send_contact_form
from src.models.api_schema import ContactFormRequest

router = APIRouter(prefix="")

router.include_router(v1_router)


@router.get("/")
async def root():
    return {"message": "Hello World!!!"}


@router.post("/contact")
async def contact_form(request: ContactFormRequest):
    return send_contact_form(request)
