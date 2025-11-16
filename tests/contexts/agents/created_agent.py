from dataclasses import dataclass
from typing import Optional

from contexts.logged_in_user import LoggedInUser
from d42 import fake
from interfaces import CodeAirAPI
from schemas.agents import NewAgentSchema, NewExternalAgentSchema

__all__ = ["created_agent", "CreatedAgent"]


@dataclass
class CreatedAgent:
    id: str
    type: str
    engine: str
    name: str
    description: str
    enabled: bool
    created_at: str
    updated_at: str
    config: dict


async def created_agent(
    user: LoggedInUser,
    project_id: int,
    agent_type: Optional[str] = None,
    engine: Optional[str] = None,
    agent_data: Optional[dict] = None,
) -> CreatedAgent:
    if agent_data is None:
        if engine == "external":
            agent_data = fake(NewExternalAgentSchema % {
                "type": agent_type or "mr-describer",
                "engine": "external",
            })
        else:
            agent_data = fake(NewAgentSchema % {
                "type": agent_type or "mr-describer",
            })

    response = await CodeAirAPI().create_agent(user.jwt_token, project_id, agent_data)
    response.raise_for_status()

    body = response.json()
    agent = body["agent"]
    return CreatedAgent(
        id=agent["id"],
        type=agent["type"],
        engine=agent["engine"],
        name=agent["name"],
        description=agent["description"],
        enabled=agent["enabled"],
        created_at=agent["created_at"],
        updated_at=agent["updated_at"],
        config=agent["config"],
    )
