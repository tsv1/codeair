from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.gitlab import added_project_member, created_gitlab_project
from d42 import fake, schema
from d42.utils import make_required
from effects import token_is_hashed, webhook_exists
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel
from schemas.agents import AgentResponseSchema, NewAgentSchema, NewExternalAgentSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, params, scenario, then, when


@scenario("Create agent (minimal fields)")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(NewAgentSchema % {
            "type": "mr-describer",
        })

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.CREATED, response.json()

        body = response.json()

        assert token_is_hashed(body["agent"]["config"]["token"], agent_data["config"]["token"])

        agent_data["config"]["token"] = body["agent"]["config"]["token"]
        assert body == schema.dict({
            "agent": AgentResponseSchema % agent_data % {
                "name": "MR Description Writer",
                "description": "Automatically generates and adds descriptions to merge requests",
            }
        })

        assert await webhook_exists(project.id, user.token)


@scenario("Create agent (all fields)")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(
            make_required(
                NewAgentSchema + schema.dict({
                    "config": make_required(NewAgentSchema["config"], ["prompt"]),
                }),
                ["name", "description"]
            )
        )

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.CREATED

        body = response.json()
        agent_data["config"]["token"] = body["agent"]["config"]["token"]
        assert body == schema.dict({
            "agent": AgentResponseSchema % agent_data
        })


@scenario("Create external agent (minimal fields)")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(NewExternalAgentSchema % {
            "type": "mr-reviewer",
            "engine": "external",
        })

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.CREATED

        body = response.json()

        assert token_is_hashed(body["agent"]["config"]["token"], agent_data["config"]["token"])

        agent_data["config"]["token"] = body["agent"]["config"]["token"]
        assert body == schema.dict({
            "agent": AgentResponseSchema % agent_data % {
                "name": "MR Code Reviewer",
                "description": "Reviews merge requests and adds comments with suggestions",
            }
        })

        assert await webhook_exists(project.id, user.token)


@scenario("Create external agent (all fields)")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(
            make_required(
                NewExternalAgentSchema + schema.dict({
                    "config": make_required(NewExternalAgentSchema["config"], ["prompt"]),
                }),
                ["name", "description"]
            )
        )

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.CREATED

        body = response.json()
        agent_data["config"]["token"] = body["agent"]["config"]["token"]
        assert body == schema.dict({
            "agent": AgentResponseSchema % agent_data
        })


@scenario("Try to create agent with invalid field {field_name}", cases=[
    params("type", "Input should be 'mr-describer' or 'mr-reviewer'"),
    params("engine", "Input should be 'pr_agent_v0.29' or 'external'"),
])
async def _(field_name: str, message: str):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(NewAgentSchema)
        agent_data[field_name] = "invalid-value"

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": f"400: Validation failed for POST /api/v1/projects/{project.id}/agents",
                "details": [{
                    "key": field_name,
                    "message": message,
                }]
            }
        }


@scenario("Try to create agent with external engine but missing external_url")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent_data = fake(NewExternalAgentSchema)
        agent_data["config"].pop("external_url")

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "BAD_REQUEST",
                "message": f"400: Validation failed for POST /api/v1/projects/{project.id}/agents",
                "details": [{
                    "message": "Value error, external_url required for external engine"
                }]
            }
        }


@scenario("Try to create agent without token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

        agent_data = fake(NewAgentSchema)

    with when:
        response = await CodeAirAPI().create_agent(jwt_token=None, project_id=project.id,
                                                   agent_data=agent_data)

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": [],
            }
        }


@scenario("Try to create agent for project where bot has no access")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

        agent_data = fake(NewAgentSchema)

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, project.id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": [],
            }
        }


@scenario("Try to create agent for non-existing project")
async def _():
    with given:
        user = await logged_in_user()
        non_existing_project_id = 999999

        agent_data = fake(NewAgentSchema)

    with when:
        response = await CodeAirAPI().create_agent(user.jwt_token, non_existing_project_id, agent_data)

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": [],
            }
        }
