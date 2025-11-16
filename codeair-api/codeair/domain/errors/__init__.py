__all__ = ["DomainError", "ValidationError", "EntityNotFoundError", "AuthenticationError"]


class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class EntityNotFoundError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass
