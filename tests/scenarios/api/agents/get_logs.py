from http import HTTPStatus

from contexts import bot_user, logged_in_user
from contexts.agents import created_agent
from contexts.gitlab import added_project_member, created_gitlab_project
from d42 import schema
from interfaces import CodeAirAPI
from libs.gitlab import GitLabAccessLevel
from vedro import given, scenario, then, when


@scenario("Get agent logs (empty)")
async def _():
    with given:
        user = await logged_in_user()
        project = await created_gitlab_project(user)
        bot = await bot_user()
        await added_project_member(project, bot.id, GitLabAccessLevel.MAINTAINER, user.token)

        agent = await created_agent(user, project.id)

    with when:
        response = await CodeAirAPI().get_agent_logs(user.jwt_token, project.id, agent.id)

    with then:
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body == schema.dict({
            "total": schema.int(0),
            "logs": schema.list([]),
        })
