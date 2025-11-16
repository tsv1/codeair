from http import HTTPStatus

from interfaces import CodeAirAPI
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("Try to call callback with invalid code")
async def _():
    with given:
        code = ""

    with when:
        response = await CodeAirAPI().callback(code)

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": "400: Validation failed for GET /api/v1/auth/gitlab/callback?code=",
                "details": [{
                    "message": "Expected `str` of length >= 1",
                    "key": "code",
                    "source": "query",
                }]
            }
        }


@scenario("Try to call callback with incorrect code")
async def _():
    with when:
        response = await CodeAirAPI().callback("incorrect_code_12345")

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid or expired authorization code",
                "details": []
            }
        }


@scenario("Try to call callback without code")
async def _():
    with when:
        response = await CodeAirAPI().callback(code=None)

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": "400: Missing required query parameter 'code' for path /api/v1/auth/gitlab/callback",
                "details": []
            }
        }
