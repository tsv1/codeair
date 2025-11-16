from http import HTTPStatus

from contexts import logged_in_user
from interfaces import CodeAirAPI
from schemas.auth import LogoutResponseSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("Logout")
async def _():
    with given:
        user = await logged_in_user()

    with when:
        response = await CodeAirAPI().logout(user.jwt_token)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == LogoutResponseSchema % {
            "message": "Successfully logged out",
        }


@scenario("Try to logout with invalid token")
async def _():
    with when:
        response = await CodeAirAPI().logout("invalid_token_12345")

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid token",
                "details": [],
            }
        }


@scenario("Try to logout without token")
async def _():
    with when:
        response = await CodeAirAPI().logout(jwt_token=None)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": [],
            }
        }
