from dataclasses import asdict
from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.agents import created_agent
from contexts.gitlab import added_project_member, created_gitlab_project
from d42 import fake, schema
from effects import token_is_hashed, webhook_exists
from helpers import delete_project_webhooks, get_project_webhooks, update_project_webhook
from interfaces import CodeAirAPI, GitLabAPI
from libs.gitlab import GitLabAccessLevel
from schemas.agents import AgentResponseSchema, NewAgentSchema, NewExternalAgentSchema
from schemas.errors import ErrorResponseSchema
from vedro import given, params, scenario, then, when


@scenario("Update agent {field_name}", cases=[
    params(field_name="name"),
    params(field_name="description"),
    params(field_name="enabled"),
])
async def _(field_name: str):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        orig_token = fake(NewAgentSchema["config"]["token"])
        agent = await created_agent(user, project.id, config={
            "token": orig_token
        })
        update_data = {
            **asdict(agent),
            field_name: fake(AgentResponseSchema[field_name])
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **update_data,
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert token_is_hashed(body["agent"]["config"]["token"], orig_token)

        assert await webhook_exists(project.id, user.token)


@scenario("Update agent config {config_field}", cases=[
    params(config_field="provider"),
    params(config_field="model"),
    params(config_field="prompt"),
    params(config_field="external_url")
])
async def _(config_field: str):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        orig_token = fake(NewAgentSchema["config"]["token"])
        agent = await created_agent(user, project.id, engine="external", config={
            "token": orig_token
        })
        update_data = {
            **asdict(agent),
            "config": {
                **agent.config,
                config_field: fake(NewExternalAgentSchema["config"][config_field])
            }
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **update_data,
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert token_is_hashed(body["agent"]["config"]["token"], orig_token)

        assert await webhook_exists(project.id, user.token)


@scenario("Update agent when webhook was deleted")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

        await delete_project_webhooks(project.id, user.token)

        update_data = {
            **asdict(agent),
            "name": fake(AgentResponseSchema["name"])
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **update_data,
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert await webhook_exists(project.id, user.token)


@scenario("Update agent when webhook config was modified")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

        webhooks = await get_project_webhooks(project.id, user.token)
        await update_project_webhook(project.id, webhooks[0]["id"], user.token,
                                     merge_requests_events=False)

        update_data = {
            **asdict(agent),
            "description": fake(AgentResponseSchema["description"])
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **update_data,
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert await webhook_exists(project.id, user.token)


@scenario("Update agent config with new token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)
        new_token = fake(NewAgentSchema["config"]["token"])

    with when:
        response = await CodeAirAPI().update_agent(
            user.jwt_token, project.id, agent.id,
            {
                **asdict(agent),
                "config": {
                    **agent.config,
                    "token": new_token,
                }
            }
        )

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **asdict(agent),
                "config": {
                    **agent.config,
                    "token": body["agent"]["config"]["token"],  # Use returned hashed token
                },
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert body["agent"]["config"]["token"] != agent.config["token"]  # Should be changed
        assert token_is_hashed(body["agent"]["config"]["token"], new_token)


@scenario("Update agent config but keep existing token (send hash)")
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

        existing_token_hash = agent.config["token"]

    with when:
        response = await CodeAirAPI().update_agent(
            user.jwt_token, project.id, agent.id,
            {
                **asdict(agent),
                "config": {
                    **agent.config,
                    "token": existing_token_hash,
                }
            }
        )

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **asdict(agent),
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })

        assert body["agent"]["config"]["token"] == agent.config["token"]  # Should be unchanged
        assert token_is_hashed(body["agent"]["config"]["token"], orig_token)


@scenario("Try to update non-updatable field {field_name}", cases=[
    params(field_name="id"),
    params(field_name="type"),
])
async def _(field_name: str):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)
        update_data = {
            **asdict(agent),
            field_name: fake(AgentResponseSchema[field_name])
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        # Field should remain unchanged
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **asdict(agent),
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })


@scenario("Try to update non-updatable fields {field_name}", cases=[
    params("engine", "pr_agent_v0.29"),
    params("created_at", "1970-01-01T00:00:00Z"),
])
async def _(field_name: str, field_value):
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id, engine="external")
        update_data = {
            **asdict(agent),
            field_name: field_value
        }

    with when:
        response = await CodeAirAPI().update_agent(user.jwt_token, project.id, agent.id, update_data)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        # Field should remain unchanged
        assert body == schema.dict({
            "agent": AgentResponseSchema % {
                **asdict(agent),
                "updated_at": body["agent"]["updated_at"],  # Ignore updated_at value
            }
        })


@scenario("Try to update non-existing agent")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)
        agent.id = "00000000-0000-0000-0000-000000000000"

    with when:
        response = await CodeAirAPI().update_agent(
            jwt_token=user.jwt_token,
            project_id=project.id,
            agent_id=agent.id,
            agent_data={
                **asdict(agent),
                "name": "Updated Name"
            }
        )

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Agent not found",
                "details": []
            }
        }


@scenario("Try to update agent without token")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

    with when:
        response = await CodeAirAPI().update_agent(
            jwt_token=None, project_id=project.id, agent_id=agent.id,
            agent_data={
                **asdict(agent),
                "name": "Updated Name"
            }
        )

    with then:
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "No JWT token found in request header",
                "details": []
            }
        }


@scenario("Try to update agent for project where bot has no access")
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
        response = await CodeAirAPI().update_agent(
            jwt_token=user.jwt_token,
            project_id=project.id,
            agent_id=agent.id,
            agent_data={
                **asdict(agent),
                "name": "Updated Name"
            }
        )

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }


@scenario("Try to update agent for non-existing project")
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
        response = await CodeAirAPI().update_agent(
            jwt_token=user.jwt_token,
            project_id=non_existing_project_id,
            agent_id=agent.id,
            agent_data={
                **asdict(agent),
                "name": "Updated Name"
            }
        )

    with then:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == ErrorResponseSchema % {
            "error": {
                "code": "NOT_FOUND",
                "message": "Project not found",
                "details": []
            }
        }
