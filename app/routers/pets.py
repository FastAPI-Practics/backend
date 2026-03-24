from typing import Annotated, Sequence

from fastapi import APIRouter, Query

from app.core.responses import auth_responses
from app.core.security import AccessTokenDep
from app.dependencies.repositories import PetRepositoryDep
from app.models.pets import PetModel
from app.schemas.base import CommonListFilters

router = APIRouter(prefix='/pets', tags=['pets'], responses=auth_responses)


@router.get('/')
async def get_pets(
    pet_repository: PetRepositoryDep,
    filters: Annotated[CommonListFilters, Query()],
    _: AccessTokenDep,
) -> Sequence[PetModel]:
    return await pet_repository.fetch(
        offset=filters.offset,
        limit=filters.limit,
    )


@router.post('/')
async def create_pets(
    pet: PetModel,
    pet_repository: PetRepositoryDep,
    _: AccessTokenDep,
) -> PetModel:
    return await pet_repository.save(pet)
