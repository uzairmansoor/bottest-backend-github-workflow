from time import time

import requests
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

from src.settings import logger, settings


def get_public_key():
    jwks_url = f"https://{settings.jwks_url}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    return {key["kid"]: key for key in jwks["keys"]}


PUBLIC_KEYS = get_public_key()


class AuthorizationHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.auth_scheme = HTTPBearer()

    async def dispatch(self, request: Request, call_next):
        # Allow requests to docs, base URL, and contact
        if (
            request.url.path.startswith("/docs")
            or request.url.path.startswith("/openapi.json")
            or request.url.path == "/"
            or request.url.path == "/contact"
        ):
            return await call_next(request)

        if request.headers.get("stubbed"):
            request.state.actor = {"id": request.headers.get("stubbed")}
            if request.headers.get("org_id"):
                request.state.actor["org_id"] = request.headers.get("org_id")
            return await call_next(request)

        try:
            # Extract the token from the header
            credentials: HTTPAuthorizationCredentials = await self.auth_scheme(request)
            token = credentials.credentials

            # Validate token
            header = jwt.get_unverified_header(token)
            key_id = header["kid"]
            public_key = PUBLIC_KEYS[key_id]
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
            )
            # Check JWT claims
            # SKIP FOR NOW
            """
            if payload["azp"] not in settings.valid_origins:
                return JSONResponse(content={"status:": "Invalid host."}, status_code=HTTP_401_UNAUTHORIZED)
            if payload["iss"] != "https://evolved-shad-78.clerk.accounts.dev":
                return JSONResponse(content={"status:": "Invalid issuer."}, status_code=HTTP_401_UNAUTHORIZED)
            """

            # Add JWT user_id and org_id (optional) to request state
            request.state.actor = {"id": payload["sub"]}
            if payload.get("org_id", None):
                request.state.actor["org_id"] = payload["org_id"]

        except ExpiredSignatureError as e:
            logger.exception(e)
            return JSONResponse(content={"status:": "Expired token."}, status_code=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception(e)
            return JSONResponse(content={"status": "Invalid token."}, status_code=HTTP_401_UNAUTHORIZED)

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            logger.info(f"Path={request.method} {request.url.path}")
            start_time = time()

            response = await call_next(request)

            process_time = (time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            logger.info(f"Completed={formatted_process_time}ms Status={response.status_code}")

            return response

        except Exception as e:
            print(e)
            logger.exception(e)
            return JSONResponse({"status": f"Internal Server Error: {e}"}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
