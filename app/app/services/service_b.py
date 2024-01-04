from uuid import UUID

from app.schemas import StudentSchema
from app.services.base_client import BaseClient


class ServiceB(BaseClient):
    async def get_students(self, ids: set[str]) -> list[StudentSchema]:
        response = await self._get("/students", params={"ids": ",".join(ids)})

        validated_response = [
            StudentSchema.model_validate(in_obj) for in_obj in response
        ]
        return validated_response


service_b = ServiceB("http://127.0.0.1:8001/api")
