from src.app import create_app
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.middleware import AuthorizationHeaderMiddleware
from src.core.utils import _generic_has_permissions
import pytest


async def mocked_dispatch(self, request, call_next):
    return await call_next(request)


@pytest.fixture(scope="session", autouse=True)
def mock_dispatch_method():
    with patch.object(AuthorizationHeaderMiddleware, "dispatch", new=mocked_dispatch):
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_has_permissions():
    with patch("src.core.utils._generic_has_permissions") as mocked_func:
        mocked_func.return_value = True
        yield


app = create_app()
client = TestClient(app)
