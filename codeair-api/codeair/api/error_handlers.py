from codeair.domain.errors import AuthenticationError, DomainError, EntityNotFoundError
from codeair.domain.errors import ValidationError as DomainValidationError
from litestar import Request, Response
from litestar.exceptions import HTTPException, ValidationException
from litestar.status_codes import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

__all__ = ["validation_exception_handler", "http_exception_handler", "generic_exception_handler", "domain_exception_handler"]


def _create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: list[dict] | None = None
) -> Response:
    return Response(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or []
        }
    })


def validation_exception_handler(request: Request, exc: ValidationException) -> Response:
    return _create_error_response(
        status_code=HTTP_400_BAD_REQUEST,
        error_code="BAD_REQUEST",
        message=str(exc),
        details=exc.extra or []
    )


def domain_exception_handler(request: Request, exc: DomainError) -> Response:
    if isinstance(exc, AuthenticationError):
        status_code = HTTP_401_UNAUTHORIZED
        error_code = "UNAUTHORIZED"
    elif isinstance(exc, EntityNotFoundError):
        status_code = HTTP_404_NOT_FOUND
        error_code = "NOT_FOUND"
    elif isinstance(exc, DomainValidationError):
        status_code = HTTP_400_BAD_REQUEST
        error_code = "BAD_REQUEST"
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "INTERNAL_ERROR"

    return _create_error_response(
        status_code=status_code,
        error_code=error_code,
        message=str(exc)
    )


def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> Response:
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_ERROR"
    }

    error_code = error_codes.get(exc.status_code, "ERROR")

    return _create_error_response(
        status_code=exc.status_code,
        error_code=error_code,
        message=exc.detail or str(exc),
        details=exc.extra if hasattr(exc, "extra") else [],
    )


def generic_exception_handler(request: Request, exc: Exception) -> Response:
    print(
        f"Unhandled exception for request {request.method} {request.url}",
        type(exc),
        exc
    )
    return _create_error_response(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred"
    )
