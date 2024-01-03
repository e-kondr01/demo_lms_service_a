from uuid import UUID

from pydantic import BaseModel


class UnitSchema(BaseModel):
    id: UUID
    name: str


class StudentSchema(BaseModel):
    id: UUID
    name: str


class StudentProgressSchema(BaseModel):
    current_unit: UnitSchema
    student: StudentSchema
