from fastapi import APIRouter, FastAPI

from app.routers import pets, users

api_prefix = '/api'

app = FastAPI(
    openapi_url=f'{api_prefix}/openapi.json',
    docs_url=f'{api_prefix}/docs',
    redoc_url=f'{api_prefix}/redoc',
)

app_router = APIRouter(prefix=f'{api_prefix}/v1')
app_router.include_router(users.router)
app_router.include_router(pets.router)

app.include_router(app_router)
