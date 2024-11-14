from uuid import UUID

from app.config import settings
from app.schemas import StudentSchema
from app.services.base_client import BaseClient


class ServiceB(BaseClient):
    async def get_students(self, ids: set[str], **kwargs) -> dict[UUID, StudentSchema]:
        params = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                params[key] = value
        response = await self._get("/students", params=params)

        students_by_id = {}
        for student in response:
            student_schema = StudentSchema.model_validate(student)
            students_by_id[student_schema.id] = student_schema
        return students_by_id

    async def get_student_ids(self, ids: set[str], **kwargs) -> list[UUID]:
        params = {"ids": ",".join(ids)}
        for key, value in kwargs.items():
            if value:
                params[key] = value
        response = await self._get("/students/ids", params=params)
        return [UUID(result_item) for result_item in response]


service_b = ServiceB(settings.SERVICE_B_HOST + "/api")
