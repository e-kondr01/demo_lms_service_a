from uuid import UUID

from pydantic import BaseModel


class StudentProgressSchema(BaseModel):
    current_unit_id: UUID
    student_id: UUID
