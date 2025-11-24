from d42 import schema

from schemas.auth import UserSchema

__all__ = ["ProjectItemSchema", "ProjectSearchResponseSchema", "ProjectDetailResponseSchema"]

ProjectItemSchema = schema.dict({
    "id": schema.int.min(1),
    "name": schema.str.len(1, ...),
    "name_with_namespace": schema.str.len(1, ...),
    "description": schema.str | schema.none,
    "visibility": schema.str.len(1, ...),
    "path": schema.str.len(1, ...),
    "path_with_namespace": schema.str.len(1, ...),
    "web_url": schema.str.len(1, ...),
    "created_at": schema.str.len(1, ...),
    "last_activity_at": schema.str.len(1, ...),
    "avatar_url": schema.str | schema.none,
})

ProjectSearchResponseSchema = schema.dict({
    "total": schema.int.min(0),
    "items": schema.list(ProjectItemSchema),
    "bot_user": UserSchema,
})

ProjectDetailResponseSchema = schema.dict({
    "project": ProjectItemSchema,
})
