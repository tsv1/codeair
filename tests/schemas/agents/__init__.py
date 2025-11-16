from d42 import optional, schema
from d42.utils import make_required
from schemas.utils import TimestampSchema, URLSchema, UUIDv4Schema

__all__ = [
    "NewAgentSchema",
    "NewExternalAgentSchema",
    "AgentResponseSchema",
    "AgentsListResponseSchema",
]

AgentConfigSchema = schema.dict({
    "provider": schema.str("anthropic"),
    "model": schema.str.len(1, ...),
    "token": schema.str.len(1, ...),
    optional("prompt"): schema.str,
})

AgentExternalConfigSchema = AgentConfigSchema + schema.dict({
    "external_url": URLSchema,
})

NewAgentSchema = schema.dict({
    optional("id"): UUIDv4Schema,
    "type": schema.str("mr-describer") | schema.str("mr-reviewer"),
    "engine": schema.str("pr_agent_v0.29"),
    optional("name"): schema.str.len(1, ...),
    optional("description"): schema.str.len(1, ...),
    "config": AgentConfigSchema,
})

NewExternalAgentSchema = NewAgentSchema + schema.dict({
    "engine": schema.str("external"),
    "config": AgentExternalConfigSchema
})

AnyNewAgentSchema = NewAgentSchema + schema.dict({
    "engine": schema.str("pr_agent_v0.29") | schema.str("external"),
    "config": schema.any(AgentConfigSchema, AgentExternalConfigSchema),
})

AgentResponseSchema = make_required(AnyNewAgentSchema, ["id", "name", "description"]) + schema.dict({
    "config": schema.any(
        AgentConfigSchema + schema.dict({
            "prompt": AgentConfigSchema["prompt"] | schema.none,
            "external_url": schema.none,
        }),
        AgentExternalConfigSchema + schema.dict({
            "prompt": AgentExternalConfigSchema["prompt"] | schema.none,
            "external_url": AgentExternalConfigSchema["external_url"],
        }),
    ),
    "enabled": schema.bool,
    "created_at": TimestampSchema,
    "updated_at": TimestampSchema,
})

AgentsListResponseSchema = schema.dict({
    "total": schema.int.min(0),
    "agents": schema.list(AgentResponseSchema),
})
