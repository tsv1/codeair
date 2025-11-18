from dataclasses import asdict
from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.agents import created_agent
from contexts.gitlab import added_project_member, created_gitlab_project
from d42 import fake
from effects import token_is_hashed
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel
from schemas.agents import AgentsListResponseSchema, NewAgentSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("List agents for project with no agents")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

    with when:
        response = await CodeAirAPI().list_agents(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == AgentsListResponseSchema % {
            "total": 0,
            "agents": [],
        }


@scenario("List agents for project with one agent")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        orig_token = fake(NewAgentSchema["config"]["token"])
        agent = await created_agent(user, project.id, config={
            "token": orig_token
        })

    with when:
        response = await CodeAirAPI().list_agents(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == AgentsListResponseSchema % {
            "total": 1,
            "agents": [
                asdict(agent)
            ]
        }

        assert token_is_hashed(body["agents"][0]["config"]["token"], orig_token)


@scenario("List agents for project with multiple agents")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        # Create first agent
        agent1 = await created_agent(user, project.id, agent_type="mr-describer")

        # Create second agent (external)
        agent2 = await created_agent(user, project.id, agent_type="mr-reviewer", engine="external")

    with when:
        response = await CodeAirAPI().list_agents(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == AgentsListResponseSchema % {
            "total": 2,
            "agents": [
                asdict(agent2),
                asdict(agent1),
            ]
        }


@scenario("Try to list agents without token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

    with when:
        response = await CodeAirAPI().list_agents(jwt_token=None, project_id=project.id)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": []
            }
        }


@scenario("Try to list agents for project where bot has no access")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

    with when:
        response = await CodeAirAPI().list_agents(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }


@scenario("Try to list agents for non-existing project")
async def _():
    with given:
        user = await logged_in_user()
        non_existing_project_id = 999999

    with when:
        response = await CodeAirAPI().list_agents(user.jwt_token, non_existing_project_id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }
