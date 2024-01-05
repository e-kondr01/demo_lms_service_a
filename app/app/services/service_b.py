from uuid import UUID

from app.schemas import StudentSchema
from app.services.base_client import BaseClient


class ServiceB(BaseClient):
    async def get_students(self, ids: set[str], **kwargs) -> list[StudentSchema]:
        params = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                params[key] = value
        response = await self._get("/students", params=params)

        validated_response = [
            StudentSchema.model_validate(in_obj) for in_obj in response
        ]
        return validated_response

    async def get_student_ids(self, ids: set[str], **kwargs) -> list[UUID]:
        params = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                params[key] = value
        response = await self._get("/students/ids", params=params)
        return [UUID(result_item) for result_item in response]


service_b = ServiceB("http://127.0.0.1:8001/api")
