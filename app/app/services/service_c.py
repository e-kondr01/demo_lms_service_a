from uuid import UUID

from app.config import settings
from app.schemas import UnitSchema
from app.services.base_client import BaseClient


class ServiceС(BaseClient):
    async def get_units(self, ids: set[str], **kwargs) -> dict[UUID, UnitSchema]:
        params = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                params[key] = value
        response = await self._get("/units", params=params)

        units_by_id = {}
        for unit in response:
            unit_schema = UnitSchema.model_validate(unit)
            units_by_id[unit_schema.id] = unit_schema
        return units_by_id

    async def get_unit_ids(self, ids: set[str], **kwargs) -> list[UUID]:
        body = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                body[key] = str(value)
        response = await self._post("/units/ids", json=body)
        return [UUID(result_item) for result_item in response]


service_c = ServiceС(settings.SERVICE_C_HOST + "/api")
