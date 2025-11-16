from d42 import schema

__all__ = ["TimestampSchema", "UUIDv4Schema", "URLSchema"]

TimestampSchema = schema.str.regex(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}")

UUIDv4Schema = schema.str.regex(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

URLSchema = schema.str.regex(r"https?://[a-z0-9]+\.[a-z]{2,}(/[a-z]+)")

