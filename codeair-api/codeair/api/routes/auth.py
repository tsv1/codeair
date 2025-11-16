from typing import Annotated, Any

from litestar import Request, Response, Router, get, post
from litestar.params import Body, Parameter
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from pydantic import BaseModel, Field

from codeair.domain.users import User
from codeair.services import AuthService

__all__ = ["auth_router"]


class AuthorizeResponse(BaseModel):
    authorization_url: str


class TokenResponse(BaseModel):
    token: str


class TokenExchangeRequest(BaseModel):
    token: str = Field(min_length=1)


class AuthResponse(BaseModel):
    user: User
    token: str


class UserResponse(BaseModel):
    user: User


class LogoutResponse(BaseModel):
    message: str


@get("/api/v1/auth/gitlab/authorize")
async def gitlab_authorize(
    auth_service: AuthService
) -> Response[AuthorizeResponse]:
    authorization_url = auth_service.get_gitlab_authorization_url()
    return Response(
        content=AuthorizeResponse(authorization_url=authorization_url),
        status_code=HTTP_200_OK,
    )


@get("/api/v1/auth/gitlab/callback")
async def gitlab_callback(
    code: Annotated[str, Parameter(min_length=1)],
    auth_service: AuthService,
) -> Response[AuthResponse]:
    token, user = await auth_service.authenticate_with_oauth_code(code=code)
    return Response(
        content=AuthResponse(token=token, user=user),
        status_code=HTTP_201_CREATED,
    )


@post("/api/v1/auth/gitlab/token")
async def gitlab_exchange_token(
    data: Annotated[TokenExchangeRequest, Body()],
    auth_service: AuthService,
) -> Response[AuthResponse]:
    token, user = await auth_service.authenticate_with_gitlab_token(data.token)
    return Response(
        content=AuthResponse(token=token, user=user),
        status_code=HTTP_201_CREATED,
    )


@get("/api/v1/auth/me")
async def get_current_user(request: Request[User, Token, Any]) -> Response[UserResponse]:
    return Response(
        content=UserResponse(user=request.user),
        status_code=HTTP_200_OK,
    )


@post("/api/v1/auth/logout")
async def logout() -> Response[LogoutResponse]:
    return Response(
        content=LogoutResponse(message="Successfully logged out"),
        status_code=HTTP_200_OK,
    )


auth_router = Router(
    path="",
    route_handlers=[
        gitlab_authorize,
        gitlab_callback,
        gitlab_exchange_token,
        get_current_user,
        logout,
    ],
)
