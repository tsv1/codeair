from dataclasses import asdict
from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.gitlab import added_project_member, created_gitlab_project
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel, ProjectVisibility
from schemas.errors import ErrorResponseSchema
from schemas.projects import ProjectSearchResponseSchema
from vedro import given, params, scenario, then, when


@scenario(
    "Search for {visibility} project without bot as member",
    cases=[
        params(visibility=ProjectVisibility.PRIVATE),
        params(visibility=ProjectVisibility.INTERNAL),
        params(visibility=ProjectVisibility.PUBLIC),
    ]
)
async def _(visibility: ProjectVisibility):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user, visibility=visibility)
        bot = await bot_user()

    with when:
        response = await CodeAirAPI().search_projects(user.jwt_token, query=project.name)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == ProjectSearchResponseSchema % {
            "total": 0,
            "items": [],
            "bot_user": asdict(bot)
        }


@scenario(
    "Search for {visibility} project with bot as member",
    cases=[
        params(visibility=ProjectVisibility.PRIVATE),
        params(visibility=ProjectVisibility.INTERNAL),
        params(visibility=ProjectVisibility.PUBLIC),
    ]
)
async def _(visibility: ProjectVisibility):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user, visibility=visibility)
        bot = await bot_user()

        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

    with when:
        response = await CodeAirAPI().search_projects(user.jwt_token, query=project.name)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == ProjectSearchResponseSchema % {
            "total": 1,
            "items": [
                {
                    "id": project.id,
                    "name": project.name,
                    "visibility": visibility.value,
                }
            ],
            "bot_user": asdict(bot)
        }


@scenario("Search for non-existing project")
async def _():
    with given:
        user = await logged_in_user()
        bot = await bot_user()
        non_existing_name = "non_existing_project_12345"

    with when:
        response = await CodeAirAPI().search_projects(user.jwt_token, query=non_existing_name)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == ProjectSearchResponseSchema % {
            "total": 0,
            "items": [],
            "bot_user": asdict(bot)
        }


@scenario("Try to search without providing q")
async def _():
    with given:
        user = await logged_in_user()

    with when:
        response = await CodeAirAPI().search_projects(user.jwt_token, query="")

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": "400: Validation failed for GET /api/v1/projects/search?q=",
                "details": [{
                    "message": "Expected `str` of length >= 1",
                    "key": "q",
                    "source": "query"
                }]
            }
        }


@scenario("Try to search without token")
async def _():
    with when:
        response = await CodeAirAPI().search_projects(jwt_token=None, query="test")

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": [],
            }
        }
