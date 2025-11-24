from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.gitlab import added_project_member, created_gitlab_project
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel
from schemas.agents import AgentsListResponseSchema
from vedro import given, scenario, then, when


@scenario("Get agent placeholders for project")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)

        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

    with when:
        response = await CodeAirAPI().get_agent_placeholders(user.jwt_token, project.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == AgentsListResponseSchema % {
            "total": 2,
            "agents": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "type": "mr-describer",
                    "engine": "pr_agent_v0.29",
                    "name": "📝 MR Description Writer",
                    "description": "Automatically generates and adds descriptions to merge requests",
                    "enabled": False,
                    "config": {
                        "provider": "anthropic",
                        "model": "anthropic/claude-3-7-sonnet-20250219",
                        "token": "-",
                        "prompt": None,
                        "external_url": None,
                    },
                },
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "type": "mr-reviewer",
                    "engine": "pr_agent_v0.29",
                    "name": "🔍 MR Code Reviewer",
                    "description": "Reviews merge requests and adds comments with suggestions",
                    "enabled": False,
                    "config": {
                        "provider": "anthropic",
                        "model": "anthropic/claude-3-7-sonnet-20250219",
                        "token": "-",
                        "prompt": None,
                        "external_url": None,
                    },
                },
            ]
        }
