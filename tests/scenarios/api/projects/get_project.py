from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.gitlab import added_project_member, created_gitlab_project
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel
from schemas.errors import ErrorResponseSchema
from schemas.projects import ProjectDetailResponseSchema
from vedro import given, scenario, then, when


@scenario("Get project info when bot has access")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()

        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

    with when:
        response = await CodeAirAPI().get_project(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == ProjectDetailResponseSchema % {
            "project": {
                "id": project.id,
                "name": project.name,
                "visibility": project.visibility.value,
            }
        }


@scenario("Get project info when bot has no access")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

    with when:
        response = await CodeAirAPI().get_project(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }


@scenario("Try to get project info without token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

    with when:
        response = await CodeAirAPI().get_project(jwt_token=None, project_id=project.id)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        body = response.json()
        assert body == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": []
            }
        }


@scenario("Get non-existing project")
async def _():
    with given:
        user = await logged_in_user()
        non_existing_id = 999999

    with when:
        response = await CodeAirAPI().get_project(user.jwt_token, non_existing_id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }
