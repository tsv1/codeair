from d42 import schema

__all__ = ["AuthorizeSchema", "AuthResponseSchema", "CurrentUserResponseSchema", "LogoutResponseSchema"]

AuthorizeSchema = schema.dict({
    "authorization_url": schema.str.len(1, ...),
})

UserSchema = schema.dict({
    "id": schema.int.min(1),
    "username": schema.str.len(1, ...),
    "name": schema.str.len(1, ...),
    "avatar_url": schema.str | schema.none,
})

AuthResponseSchema = schema.dict({
    "token": schema.str.len(1, ...),
    "user": UserSchema,
})

CurrentUserResponseSchema = schema.dict({
    "user": UserSchema,
})

LogoutResponseSchema = schema.dict({
    "message": schema.str.len(1, ...),
})
