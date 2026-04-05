from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.error_handlers import exception_handler
from app.core.middlewares import request_logging_middleware
from app.core.responses import common_responses
from app.core.settings import settings
from app.routers import auth, health, permissions, pets, roles, users

limiter = Limiter(key_func=get_remote_address, default_limits=['10/minute'])

api_prefix = '/api'


app = FastAPI(
    openapi_url=f'{api_prefix}/openapi.json' if settings.common.debug else None,
    docs_url=f'{api_prefix}/docs' if settings.common.debug else None,
    redoc_url=f'{api_prefix}/redoc' if settings.common.debug else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

origins = [settings.common.host]

app.add_exception_handler(exc_class_or_status_code=Exception, handler=exception_handler)

app_router = APIRouter(prefix=f'{api_prefix}/v1', responses=common_responses)
app_router.include_router(users.router)
app_router.include_router(pets.router)
app_router.include_router(auth.router)
app_router.include_router(permissions.router)
app_router.include_router(roles.router)
app_router.include_router(health.router)

app.include_router(app_router)
app.middleware('http')(request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allow_headers=['Authorization', 'Content-Type', 'X-Requested-With'],
    max_age=3600,  # Cache preflight requests for 1 hour
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title='Vet clinic',
        version='1.0.0',
        description='Custom description',
        routes=app.routes,
        servers=[
            {'url': settings.common.host, 'description': 'Local server'},
            {
                'url': 'https://vet-clinic.itis-sel.com',
                'description': 'Production server',
            },
        ],
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
