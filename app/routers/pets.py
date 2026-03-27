from typing import Annotated, Sequence

from fastapi import APIRouter, Query, Security

from app.core.responses import auth_responses
from app.dependencies.auth import get_current_user
from app.dependencies.repositories import PetRepositoryDep
from app.models.pets import PetModel
from app.schemas.base import CommonListFilters

router = APIRouter(prefix='/pets', tags=['pets'], responses=auth_responses)


@router.get(path='/', dependencies=[Security(get_current_user, scopes=['pets:list'])])
async def get_pets(
    pet_repository: PetRepositoryDep,
    filters: Annotated[CommonListFilters, Query()],
) -> Sequence[PetModel]:
    return await pet_repository.fetch(
        offset=filters.offset,
        limit=filters.limit,
    )


@router.post(
    path='/', dependencies=[Security(get_current_user, scopes=['pets:create'])]
)
async def create_pets(
    pet: PetModel,
    pet_repository: PetRepositoryDep,
) -> PetModel:
    return await pet_repository.save(pet)
