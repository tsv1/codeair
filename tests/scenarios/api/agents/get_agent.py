import json
from dataclasses import asdict
from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.agents import created_agent
from contexts.gitlab import added_project_member, created_gitlab_project
from d42 import schema
from interfaces import CodeAirAPI, GitLabAPI
from libs.gitlab import GitLabAccessLevel
from schemas.agents import AgentResponseSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, scenario, then, when


@scenario("Get agent by ID")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

    with when:
        response = await CodeAirAPI().get_agent(user.jwt_token, project.id, agent.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % asdict(agent)
        })


@scenario("Get external agent by ID")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id, engine="external")

    with when:
        response = await CodeAirAPI().get_agent(user.jwt_token, project.id, agent.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % asdict(agent)
        })


@scenario("Try to get non-existing agent")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        non_existing_agent_id = "00000000-0000-0000-0000-000000000000"

    with when:
        response = await CodeAirAPI().get_agent(user.jwt_token, project.id, non_existing_agent_id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Agent not found",
                "details": []
            }
        }


@scenario("Try to get agent without token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

    with when:
        response = await CodeAirAPI().get_agent(jwt_token=None, project_id=project.id,
                                                agent_id=agent.id)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": []
            }
        }


@scenario("Try to get agent for project where bot has no access")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()

        # Give bot access, create agent, then remove access
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)
        agent = await created_agent(user, project.id)
        await GitLabAPI().remove_project_member(project.id, bot.id, user.token)

    with when:
        response = await CodeAirAPI().get_agent(user.jwt_token, project.id, agent.id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": [],
            }
        }


@scenario("Try to get agent for non-existing project")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        # Create a real agent
        agent = await created_agent(user, project.id)

        # But try to access it with non-existing project ID
        non_existing_project_id = 999999

    with when:
        response = await CodeAirAPI().get_agent(user.jwt_token, non_existing_project_id,
                                                agent.id)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }
