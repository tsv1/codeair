from http import HTTPStatus

from contexts import logged_in_user
from interfaces import CodeAirAPI
from schemas.auth import CurrentUserResponseSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("Get current user info")
async def _():
    with given:
        user = await logged_in_user()

    with when:
        response = await CodeAirAPI().get_user_info(user.jwt_token)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == CurrentUserResponseSchema % {
            "user": {
                "id": user.user_id,
                "username": user.username,
                "name": user.name,
                "avatar_url": user.avatar_url,
            }
        }


@scenario("Try to get current user info with invalid token")
async def _():
    with when:
        response = await CodeAirAPI().get_user_info("invalid_token_12345")

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid token",
                "details": [],
            }
        }


@scenario("Try to get current user info without token")
async def _():
    with when:
        response = await CodeAirAPI().get_user_info(jwt_token=None)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": [],
            }
        }
