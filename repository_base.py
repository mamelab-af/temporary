import asyncio
import datetime
import uuid
from collections.abc import Sequence
from math import ceil
from typing import Annotated, Any

from fastapi import HTTPException, status
from pydantic import Field, validate_call
from sqlalchemy import asc, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ca14domain.object.domain_base_model import DomainBaseModel
from app.ca14domain.repository.types.list_response_base import ListResponseBase
from app.ca21gateway.orm.types.orm_base_model import ORMBaseModel
from app.ca21gateway.repository.types.list_request import ListRequest


class RepositoryBase[ORMType: ORMBaseModel]:
  def __init__(self, session: AsyncSession, orm_type: type[ORMType]) -> None:
    self.__session = session
    self.__orm_type = orm_type

  async def _base_find_by_id(
    self,
    target_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    stmt = select(self.__orm_type).where(self.__orm_type.id == target_id)
    result = await self.__session.execute(stmt)
    scalar_data = result.scalar()
    return scalar_data.__dict__ if scalar_data is not None else None

  async def _base_list(self, req: ListRequest) -> ListResponseBase[dict[str, Any]]:
    # get total count
    get_count_stmt = select(func.count().over().label("total_count")).select_from(self.__orm_type).distinct()
    get_count_stmt = req.additional_query(get_count_stmt)
    got_count_result = await self.__session.execute(get_count_stmt)
    got_count_row = got_count_result.first()
    if got_count_row:
      total_count = got_count_row[0]
      total_pages = ceil(total_count / req.page_size)
    else:
      total_count = 0
      total_pages = 1

    # get records
    get_records_stmt = select(self.__orm_type).distinct()
    get_records_stmt = req.additional_query(get_records_stmt)

    if req.sort_columns:
      column_names = self.__orm_type.__table__.columns.keys()
      for name, direction in req.sort_columns.items():
        if name not in column_names:
          raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"invalid sort key. key: '{name}'",
          )

        get_records_stmt = get_records_stmt.order_by(asc(name) if direction == "asc" else desc(name))  # noqa: F821

    get_records_stmt = get_records_stmt.offset((req.page_num - 1) * req.page_size).limit(req.page_size)

    got_records_result = await self.__session.scalars(get_records_stmt)
    got_records = got_records_result.unique().all()

    return ListResponseBase[dict[str, Any]](
      items=[record.__dict__ for record in got_records],
      metadata=ListResponseBase.Metadata(
        current_page=req.page_num,
        page_size=req.page_size,
        total_items=total_count,
        total_pages=total_pages,
        has_next=req.page_num < total_pages,
        has_previous=req.page_num > 1,
      ),
    )

  async def _base_inserts(
    self,
    user_id: uuid.UUID,
    records: Sequence[dict[str, Any]],
  ) -> Sequence[dict[str, Any]]:
    if not records:
      return []

    now = datetime.datetime.now(tz=datetime.UTC)

    def build_dict(record: dict[str, Any]) -> dict[str, Any]:
      record["created_at"] = now
      record["created_by"] = user_id
      record["updated_at"] = now
      record["updated_by"] = user_id
      return record

    records_dict = [build_dict(record) for record in records]

    result = await self.__session.execute(
      insert(self.__orm_type).returning(self.__orm_type, sort_by_parameter_order=True),
      records_dict,
    )
    scalars = result.scalars().all()

    if len(scalars) != len(records):
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="failed to insert record",
      )

    return [scalar.__dict__ for scalar in scalars]

  async def _base_updates(
    self,
    user_id: uuid.UUID,
    records: Sequence[dict[str, Any]],
  ) -> Sequence[dict[str, Any]]:
    if not records:
      return []

    now = datetime.datetime.now(tz=datetime.UTC)

    def build_dict(record: dict[str, Any]) -> dict[str, Any]:
      record["updated_at"] = now
      record["updated_by"] = user_id
      return record

    records_dict = [build_dict(record) for record in records]

    _ = await self.__session.execute(
      update(self.__orm_type),
      records_dict,
    )

    ids = [record["id"] for record in records if record.get("id") is not None]
    result = await self.__session.scalars(
      select(self.__orm_type).where(self.__orm_type.id.in_(ids)).execution_options(include_deleted=True),
    )

    scalars = result.all()

    if len(scalars) != len(records):
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="failed to update record",
      )

    return [scalar.__dict__ for scalar in scalars]

  @validate_call(validate_return=True)
  async def _base_save(
    self,
    user_id: uuid.UUID,
    records: Annotated[Sequence[dict[str, Any]], Field(min_length=1)],
  ) -> Sequence[dict[str, Any]]:
    result_records_list = await asyncio.gather(
      self._base_inserts(user_id, [record for record in records if record.get("id") is None]),
      self._base_updates(user_id, [record for record in records if record.get("id") is not None]),
    )

    flatten_result_records: list[dict[str, Any]] = []
    for result_records in result_records_list:
      flatten_result_records.extend(result_records)
    return flatten_result_records

  @validate_call(validate_return=True)
  async def _base_deletes(
    self,
    user_id: uuid.UUID,
    target_ids: Annotated[Sequence[uuid.UUID], Field(min_length=1)],
  ) -> Sequence[dict[str, Any]]:
    now = datetime.datetime.now(tz=datetime.UTC)

    def build_dict(target_id: uuid.UUID) -> dict[str, Any]:
      record = DomainBaseModel()
      record.id = target_id
      record.updated_at = now
      record.updated_by = user_id
      record.deleted_at = now
      record.deleted_by = user_id
      return record.model_dump(exclude_unset=True)

    records_dict = [build_dict(target_id) for target_id in target_ids]

    _ = await self.__session.execute(
      update(self.__orm_type),
      records_dict,
    )

    result = await self.__session.scalars(
      select(self.__orm_type).where(self.__orm_type.id.in_(target_ids)).execution_options(include_deleted=True),
    )

    scalars = result.all()

    if len(scalars) != len(target_ids):
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="failed to delete record",
      )

    return [scalar.__dict__ for scalar in scalars]
