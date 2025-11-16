from http import HTTPStatus

from interfaces import CodeAirAPI
from schemas.healthcheck import DetailedHealthcheckSchema, HealthcheckSchema
from vedro import scenario, then, when


@scenario("Get healthcheck")
async def _():
    with when:
        response = await CodeAirAPI().healthcheck()

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == HealthcheckSchema % {
            "status": "healthy"
        }


@scenario("Get detailed healthcheck")
async def _():
    with when:
        response = await CodeAirAPI().detailed_healthcheck()

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == DetailedHealthcheckSchema % {
            "checks": {
                "database": {"status": "ok"},
                "gitlab": {"status": "ok"},
            }
        }
