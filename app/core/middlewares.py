from fastapi import Request

from app.utils.logger import logger


async def request_logging_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(
            'Unhandled exception encountered',
            extra={
                'path': request.url.path,
                'method': request.method,
                'client_host': request.client.host,
            },
            exc_info=True,
        )
        raise exc
