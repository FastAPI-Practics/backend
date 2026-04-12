from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt import PyJWTError

from app.core.responses import (
    auth_responses,
    common_responses,
    detail_responses,
    login_responses,
    register_responses,
)
from app.schemas.errors import (
    ErrorSchema,
    InternalServerErrorSchema,
    UnauthorizedErrorSchema,
)
from app.utils.logger import logger


async def exception_handler(request: Request, exc: Exception):
    extra_data = {
        'path': request.url.path,
        'method': request.method,
        'client_host': request.client.host,
    }
    logger.error(
        'Error happened',
        extra=extra_data,
        exc_info=True,
    )
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={'message': 'Validation error', 'detail': exc.errors()},
        )
    if isinstance(exc, PyJWTError):
        JSONResponse(
            status_code=401,
            content=UnauthorizedErrorSchema().model_dump(),
        )

    status_code = 500

    expected_responses = {
        **common_responses,
        **auth_responses,
        **detail_responses,
    }

    extra_responses = {**login_responses, **register_responses}

    for code, config in extra_responses.items():
        model: ErrorSchema = config.get('model', InternalServerErrorSchema)()
        error_cls = model.error_cls
        if isinstance(exc, error_cls):
            status_code = code
            break

    for code, config in expected_responses.items():
        model: ErrorSchema = config.get('model', InternalServerErrorSchema)()
        error_cls = model.error_cls
        if isinstance(exc, error_cls):
            status_code = code
            break

    return JSONResponse(
        status_code=status_code,
        content={
            'message': exc.message if hasattr(exc, 'message') else None,
            'detail': exc.detail if hasattr(exc, 'detail') else None,
        },
    )
