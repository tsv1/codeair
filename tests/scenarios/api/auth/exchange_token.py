from http import HTTPStatus

from contexts import registered_user
from contexts.gitlab import created_gitlab_access_token
from interfaces import CodeAirAPI
from schemas.auth import AuthResponseSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("Exchange token")
async def _():
    with given:
        user = await registered_user()
        token = await created_gitlab_access_token(user)

    with when:
        response = await CodeAirAPI().exchange_token(token)

    with then:
        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == AuthResponseSchema % {
            "user": {
                "id": user.user_id,
                "username": user.username,
                "name": user.name,
            }
        }


@scenario("Try to exchange token with incorrect one")
async def _():
    with given:
        token = "invalid_token_12345"

    with when:
        response = await CodeAirAPI().exchange_token(token)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid or expired GitLab token",
                "details": []
            }
        }


@scenario("Try to exchange token without providing one")
async def _():
    with when:
        response = await CodeAirAPI().exchange_token(token=None)

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": "400: Validation failed for POST /api/v1/auth/gitlab/token",
                "details": [{
                    "message": "Field required",
                    "key": "token",
                }]
            }
        }
