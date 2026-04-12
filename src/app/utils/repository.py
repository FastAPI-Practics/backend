import math
from typing import Optional, Sequence
from uuid import UUID

from generics import get_filled_type
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import func
from sqlalchemy.sql._typing import (
    _ColumnExpressionArgument,
)
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.dependencies.session import SessionDep
from app.models.base import BaseModel
from app.schemas.base import CommonListFilters
from app.utils.pagination import ListResponse, PaginationInfo

type FilterType = _ColumnExpressionArgument[bool] | bool


class Repository[Model: BaseModel]:
    __model: type[Model] | None = None
    __session: AsyncSession

    @property
    def model(self) -> type[Model]:
        if self.__model is None:
            self.__model = get_filled_type(self, Repository, 0)
        return self.__model

    def __init__(self, session: SessionDep):
        self.__session = session

    async def get(self, pk: UUID) -> Optional[Model]:
        return await self.__session.get(self.model, pk)

    def __form_select_statement(
        self,
        filters: Optional[PydanticBaseModel] = None,
        with_count: bool = False,
    ):
        select_statement = select(self.model)
        if with_count:
            select_statement = select(func.count(self.model.id))
        if filters is not None:
            filter_statement = and_(True)
            filters_dict = filters.model_dump()
            for key, value in filters_dict.items():
                if not hasattr(self.__model, key):
                    continue
                if value is not None:
                    filter_statement = and_(
                        filter_statement, getattr(self.model, key) == value
                    )
            select_statement = select_statement.where(filter_statement)
        return select_statement

    async def __exec_select(
        self,
        select_statement,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Sequence[Model]:
        if offset is not None:
            select_statement = select_statement.offset(offset)
        if limit is not None:
            select_statement = select_statement.limit(limit)
        entities = await self.__session.exec(select_statement)
        return entities.all()

    async def fetch_with_pagination_data(
        self,
        filters: CommonListFilters,
    ) -> ListResponse[Model]:
        limit = filters.limit
        offset = filters.offset

        select_statement = self.__form_select_statement(filters)
        count_statement = self.__form_select_statement(filters, with_count=True)
        total = (await self.__session.exec(count_statement)).one()
        items = await self.__exec_select(
            select_statement=select_statement, limit=limit, offset=offset
        )

        pages_num = math.ceil(total / limit)
        page = (offset // limit) + 1

        pagination_info = PaginationInfo(total=total, page=page, pages_num=pages_num)

        return ListResponse(info=pagination_info, items=items)

    async def fetch(
        self,
        filters: Optional[PydanticBaseModel] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Sequence[Model]:
        select_statement = self.__form_select_statement(filters)
        return await self.__exec_select(
            select_statement=select_statement, limit=limit, offset=offset
        )

    async def save(self, instance: Model) -> Model:
        self.__session.add(instance)
        await self.__session.commit()
        await self.__session.refresh(instance)
        return instance

    async def save_all(self, instances: list[Model]) -> list[Model]:
        self.__session.add_all(instances)
        await self.__session.commit()
        for instance in instances:
            await self.__session.refresh(instance)
        return instances

    async def delete(self, pk: UUID) -> Optional[Model]:
        instance = await self.get(pk)
        if instance is None:
            return None
        await self.__session.delete(instance)
        await self.__session.commit()
        return instance

    async def update(self, pk: UUID, updates: PydanticBaseModel) -> Optional[Model]:
        instance = await self.get(pk)
        if instance is None:
            return None
        instance_update_dump = updates.model_dump()
        for key, value in instance_update_dump.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.save(instance)
        return instance
