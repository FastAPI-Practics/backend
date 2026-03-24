from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.responses import auth_responses, common_responses, detail_responses
from app.schemas.errors import ErrorSchema, InternalServerErrorSchema


async def exception_handler(_: Request, exc: Exception):
    status_code = 500

    expected_responses = {
        **common_responses,
        **auth_responses,
        **detail_responses,
    }

    for code, config in expected_responses.items():
        model: ErrorSchema = config.get('model', InternalServerErrorSchema)()
        error_cls = model.error_cls
        if isinstance(exc, error_cls):
            status_code = code
            break

    return JSONResponse(
        status_code=status_code,
        content={
            'message': exc.message,
            'detail': exc.detail if hasattr(exc, 'detail') else None,
        },
    )
