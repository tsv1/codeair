from d42 import schema

__all__ = ["ErrorResponseSchema"]

ErrorSchema = schema.dict({
    "code": schema.str.len(1, ...),
    "message": schema.str.len(1, ...),
    "details": schema.list(schema.dict) | schema.none,
})

ErrorResponseSchema = schema.dict({
    "error": ErrorSchema
})
