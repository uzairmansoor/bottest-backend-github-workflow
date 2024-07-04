from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from mangum import Mangum

from src.api import router as api_router
from src.middleware import AuthorizationHeaderMiddleware, LoggingMiddleware
from src.settings import settings

OPENAPI_TAGS = [
    {
        "name": "Baselines",
        "description": "APIs for baselines.",
    },
    {
        "name": "Bots",
        "description": "APIs for bots.",
    },
    {
        "name": "Environments",
        "description": "APIs for environments.",
    },
    {
        "name": "Evaluations",
        "description": "APIs for evaluations.",
    },
    {
        "name": "Organizations",
        "description": "APIs for organizations.",
    },
    {
        "name": "Suite Runs",
        "description": "APIs for suite runs.",
    },
    {
        "name": "Suites",
        "description": "APIs for suites.",
    },
    {
        "name": "Test Runs",
        "description": "APIs for test runs.",
    },
    {
        "name": "Tests",
        "description": "APIs for tests.",
    },
    {
        "name": "Users",
        "description": "APIs for users.",
    },
    {
        "name": "Variant Runs",
        "description": "APIs for variant runs.",
    },
    {
        "name": "Variants",
        "description": "APIs for variants.",
    },
    {
        "name": "Analytics",
        "description": "APIs for analytics.",
    },
]


def create_app():
    app = FastAPI(
        title="bottest.ai",
        version="1.0.0",
        description="Backend API Specs for bottest.ai",
        openapi_tags=OPENAPI_TAGS,
    )
    # Routes
    app.include_router(api_router)

    # Non authorization middleware
    app.add_middleware(AuthorizationHeaderMiddleware)

    # Logging middleware
    app.add_middleware(LoggingMiddleware)

    # Add CORS middleware (last)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.valid_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )


handler = Mangum(app)
