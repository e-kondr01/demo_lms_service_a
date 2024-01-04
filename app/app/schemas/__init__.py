from uuid import UUID

from pydantic import BaseModel


class UnitSchema(BaseModel):
    id: UUID
    name: str


class InstitutionSchema(BaseModel):
    id: UUID
    name: str


class StudentSchema(BaseModel):
    id: UUID
    name: str
    institution: InstitutionSchema


class AssessmentSchema(BaseModel):
    unit: UnitSchema
    student: StudentSchema
    grade: int | None
