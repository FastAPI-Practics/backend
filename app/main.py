from fastapi import APIRouter, FastAPI

from app.routers import pets, users

app = FastAPI()
app_router = APIRouter(prefix='/api/v1')
app_router.include_router(users.router)
app_router.include_router(pets.router)

app.include_router(app_router)
