from http import HTTPStatus
from urllib.parse import urlencode

from config import Config as cfg
from interfaces import CodeAirAPI
from schemas.auth import AuthorizeSchema
from vedro import given, scenario, then, when


@scenario("Authorize")
async def _():
    with given:
        expected_params = urlencode({
            "client_id": cfg.GITLAB_OAUTH_CLIENT_ID,
            "redirect_uri": cfg.GITLAB_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "read_user",
        })
        expected_url = f"{cfg.GITLAB_URL}/oauth/authorize?{expected_params}"

    with when:
        response = await CodeAirAPI().authorize()

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == AuthorizeSchema % {
            "authorization_url": expected_url,
        }
