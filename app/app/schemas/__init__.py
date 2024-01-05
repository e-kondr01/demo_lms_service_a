from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)


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
