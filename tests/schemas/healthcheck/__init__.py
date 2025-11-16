from d42 import schema
from schemas.utils import TimestampSchema

__all__ = ["HealthcheckSchema", "DetailedHealthcheckSchema"]

HealthcheckSchema = schema.dict({
    "status": schema.str("healthy") | schema.str("degraded"),
    "service": schema.str("codeair"),
    "timestamp": TimestampSchema,
    "version": schema.str,
    "uptime_seconds": schema.int.min(1),
})

HealthCheckResultSchema = schema.dict({
    "status": schema.str("ok") | schema.str("failed"),
    "message": schema.str | schema.none,
})

DetailedHealthcheckSchema = HealthcheckSchema + schema.dict({
    "checks": schema.dict({
        "database": HealthCheckResultSchema,
        "gitlab": HealthCheckResultSchema,
    })
})
